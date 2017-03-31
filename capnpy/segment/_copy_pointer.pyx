"""
Schema-less deep-copy of a generic pointer.

Note that when we are using Cython, this is *NOT* a standalone
module. Instead, this file is textually included by builder.pyx, for
performance reasons.

SegmentBuilder is a @cython.final class, which means that whenever we do a
method call such as "allocate_struct()", Cython can insert a direct call
instead of going through the vtable.  However, this is done only if the method
call is inside the same compilation unit of the class. Thus, by including this
file inside SegmentBuilder we enable this optimization, which seems to give a
~40% performance improvement.
"""

from libc.stdint cimport int64_t
from libc.string cimport memcpy
from capnpy cimport ptr
from capnpy.packing cimport as_cbuf
from capnpy.segment.builder cimport SegmentBuilder
from capnpy.segment.base cimport BaseSegment

# =====================
# BaseSegment speedups
#
# it turns out that calling src.read_int64 and src.check_bounds add a
# significant overhead to copy_pointer, because they are expensive virtual
# calls which does not much in the body. So, we are reimplementing them here,
# in form of fast functions and macros.
#
# Together, they make a 2.1x slowdown!

cdef int64_t read_int64_fast(BaseSegment src, long i):
    return (<int64_t*>(src.cbuf+i))[0]

# check_bounds:
# this is a bit of a hack because apparently it is not possible to define the
# equivalent of C macros in Cython. Earlier, check_bound was a normal cdef
# function which raised if needed. Now, we turned check_bound into a C macro
# with a fast-path (the bound check), and we moved the slow path inside the
# raise_out_of_bound function. This seems to give a ~40% speedup!
cdef extern from "_copy_pointer.h":
    long check_bounds "CHECK_BOUNDS" (BaseSegment src, Py_ssize_t size, Py_ssize_t offset) except -1

cdef long raise_out_of_bounds(Py_ssize_t size, Py_ssize_t offset) except -1:
    raise IndexError('Offset out of bounds: %d' % (offset+size))
 
# ======================

@cython.ccall
@cython.returns(long)
@cython.except_(-1)
@cython.locals(src=BaseSegment, p=long, src_pos=long, dst=SegmentBuilder, dst_pos=long,
               kind=long)
def copy_pointer(src, p, src_pos, dst, dst_pos):
    """
    Copy from: BaseSegment src, pointer p living at the src_pos offset
           to: SegmentBuilder dst at position dst_pos
    """
    kind = ptr.kind(p)
    if kind == ptr.STRUCT:
        return _copy_struct(src, p, src_pos, dst, dst_pos)
    elif kind == ptr.LIST:
        item_size = ptr.list_size_tag(p)
        if item_size == ptr.LIST_SIZE_COMPOSITE:
            return _copy_list_composite(src, p, src_pos, dst, dst_pos)
        elif item_size == ptr.LIST_SIZE_PTR:
            return _copy_list_ptr(src, p, src_pos, dst, dst_pos)
        else:
            return _copy_list_primitive(src, p, src_pos, dst, dst_pos)
    ## elif kind == ptr.FAR:
    ##     raise NotImplementedError('Far pointer not supported')
    assert False, 'unknown ptr kind: %s' % kind


@cython.cfunc
@cython.returns(long)
@cython.except_(-1)
@cython.locals(n=long, src=BaseSegment, src_pos=long, dst=SegmentBuilder, dst_pos=long,
               i=long, p=long, offset=long)
def _copy_many_ptrs(n, src, src_pos, dst, dst_pos):
    check_bounds(src, n*8, src_pos)
    for i in range(n):
        offset = i*8
        p = read_int64_fast(src, src_pos + offset)
        if p != 0:
            copy_pointer(src, p, src_pos + offset, dst, dst_pos + offset)


@cython.cfunc
@cython.returns(long)
@cython.except_(-1)
@cython.locals(src=BaseSegment, p=long, src_pos=long, dst=SegmentBuilder, dst_pos=long,
               data_size=long, ptrs_size=long, ds=long)
def _copy_struct(src, p, src_pos, dst, dst_pos):
    src_pos = ptr.deref(p, src_pos)
    data_size = ptr.struct_data_size(p)
    ptrs_size = ptr.struct_ptrs_size(p)
    ds = data_size*8
    dst_pos = dst.alloc_struct(dst_pos, data_size, ptrs_size)
    check_bounds(src, ds, src_pos)
    dst.memcpy_from(dst_pos, src.cbuf+src_pos, ds) # copy data section
    _copy_many_ptrs(ptrs_size, src, src_pos+ds, dst, dst_pos+ds)


@cython.cfunc
@cython.returns(long)
@cython.except_(-1)
@cython.locals(src=BaseSegment, p=long, src_pos=long, dst=SegmentBuilder, dst_pos=long,
               count=long, size_tag=long, body_length=long)
def _copy_list_primitive(src, p, src_pos, dst, dst_pos):
    src_pos = ptr.deref(p, src_pos)
    count = ptr.list_item_count(p)
    size_tag = ptr.list_size_tag(p)
    body_length = 0
    if size_tag == ptr.LIST_SIZE_BIT:
        body_length = (count + 8 - 1) / 8 # divide by 8 and round up
    else:
        body_length = count * ptr.list_item_length(size_tag)
    #
    dst_pos = dst.alloc_list(dst_pos, size_tag, count, body_length)
    check_bounds(src, body_length, src_pos)
    dst.memcpy_from(dst_pos, src.cbuf+src_pos, body_length)


@cython.cfunc
@cython.returns(long)
@cython.except_(-1)
@cython.locals(src=BaseSegment, p=long, src_pos=long, dst=SegmentBuilder, dst_pos=long,
               count=long, body_length=long)
def _copy_list_ptr(src, p, src_pos, dst, dst_pos):
    src_pos = ptr.deref(p, src_pos)
    count = ptr.list_item_count(p)
    body_length = count*8
    dst_pos = dst.alloc_list(dst_pos, ptr.LIST_SIZE_PTR, count, body_length)
    check_bounds(src, body_length, src_pos)
    _copy_many_ptrs(count, src, src_pos, dst, dst_pos)


@cython.cfunc
@cython.returns(long)
@cython.except_(-1)
@cython.locals(src=BaseSegment, p=long, src_pos=long, dst=SegmentBuilder, dst_pos=long,
               total_words=long, body_length=long,
               tag=long, count=long, data_size=long, ptrs_size=long,
               i=long, item_length=long, ptrs_section_offset=long)
def _copy_list_composite(src, p, src_pos, dst, dst_pos):
    src_pos = ptr.deref(p, src_pos)
    total_words = ptr.list_item_count(p) # n of words NOT including the tag
    body_length = (total_words+1)*8      # total length INCLUDING the tag
    #
    # check that there is enough data for both the tag AND the whole body;
    # this way we do the bound checking only once
    check_bounds(src, body_length, src_pos)
    tag = read_int64_fast(src, src_pos)
    count = ptr.offset(tag)
    data_size = ptr.struct_data_size(tag)
    ptrs_size = ptr.struct_ptrs_size(tag)
    #
    # allocate the list and copy the whole body at once
    dst_pos = dst.alloc_list(dst_pos, ptr.LIST_SIZE_COMPOSITE, total_words, body_length)
    dst.memcpy_from(dst_pos, src.cbuf+src_pos, body_length)
    #
    # iterate over the elements, fix the pointers and copy the content
    i = 0
    item_length = (data_size+ptrs_size) * 8
    ptrs_section_offset = 0
    for i in range(count):
        ptrs_section_offset = 8 + item_length*i + data_size*8
        _copy_many_ptrs(ptrs_size, src,
                        src_pos + ptrs_section_offset,
                        dst,
                        dst_pos + ptrs_section_offset)
