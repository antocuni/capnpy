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

@cython.final
cdef class SrcBuffer(object):
    cdef const char* cbuf
    cdef Py_ssize_t len

    def __cinit__(self, bytes src):
        self.cbuf = as_cbuf(src, &self.len)

# this is a bit of a hack because apparently it is not possible to define the
# equivalent of C macros in Cython. Earlier, check_bound was a normal cdef
# function which raised if needed. Now, we turned check_bound into a C macro
# with a fast-path (the bound check), and we moved the slow path inside the
# raise_out_of_bound function. This seems to give a ~40% speedup!
cdef extern from "_copy_pointer.h":
    long check_bound "CHECK_BOUND" (long pos, long n, Py_ssize_t src_len) except -1

cdef long raise_out_of_bound(long pos, long n, Py_ssize_t src_len) except -1:
    msg = ("Invalid capnproto message: offset out of bound "
           "at position %s (%s > %s)" % (pos, pos+n, src_len))
    raise IndexError(msg)
 
cdef int64_t read_int64(SrcBuffer src, long i):
    return (<int64_t*>(src.cbuf+i))[0]

cpdef copy_pointer(bytes src, long p, long src_pos, SegmentBuilder dst, long dst_pos):
    """
    Copy from: buffer src, pointer p living at the src_pos offset
         to:   buffer dst at position dst_pos
    """
    cdef SrcBuffer srcbuf = SrcBuffer(src)
    _copy(srcbuf, p, src_pos, dst, dst_pos)


cdef long _copy(SrcBuffer src, long p, long src_pos,
                SegmentBuilder dst, long dst_pos) except -1:
    cdef long kind = ptr.kind(p)
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

cdef long _copy_many_ptrs(long n, SrcBuffer src, long src_pos,
                          SegmentBuilder dst, long dst_pos) except -1:
    cdef long i, p, offset
    check_bound(src_pos, n*8, src.len)
    for i in range(n):
        offset = i*8
        p = read_int64(src, src_pos + offset)
        if p != 0:
            _copy(src, p, src_pos + offset, dst, dst_pos + offset)

cdef long _copy_struct(SrcBuffer src, long p, long src_pos,
                       SegmentBuilder dst, long dst_pos) except -1:
    src_pos = ptr.deref(p, src_pos)
    cdef long data_size = ptr.struct_data_size(p)
    cdef long ptrs_size = ptr.struct_ptrs_size(p)
    cdef long ds = data_size*8
    dst_pos = dst.alloc_struct(dst_pos, data_size, ptrs_size)
    check_bound(src_pos, ds, src.len)
    dst.memcpy_from(dst_pos, src.cbuf+src_pos, ds) # copy data section
    _copy_many_ptrs(ptrs_size, src, src_pos+ds, dst, dst_pos+ds)


cdef long _copy_list_primitive(SrcBuffer src, long p, long src_pos,
                               SegmentBuilder dst, long dst_pos) except -1:
    src_pos = ptr.deref(p, src_pos)
    cdef long count = ptr.list_item_count(p)
    cdef long size_tag = ptr.list_size_tag(p)
    cdef long body_length = 0
    if size_tag == ptr.LIST_SIZE_BIT:
        body_length = (count + 8 - 1) / 8; # divide by 8 and round up
    else:
        body_length = count * ptr.list_item_length(size_tag)
    #
    dst_pos = dst.alloc_list(dst_pos, size_tag, count, body_length)
    check_bound(src_pos, body_length, src.len)
    dst.memcpy_from(dst_pos, src.cbuf+src_pos, body_length)

cdef long _copy_list_ptr(SrcBuffer src, long p, long src_pos,
                         SegmentBuilder dst, long dst_pos) except -1:
    src_pos = ptr.deref(p, src_pos)
    cdef long count = ptr.list_item_count(p)
    cdef long body_length = count*8
    dst_pos = dst.alloc_list(dst_pos, ptr.LIST_SIZE_PTR, count, body_length)
    check_bound(src_pos, body_length, src.len)
    _copy_many_ptrs(count, src, src_pos, dst, dst_pos)


cdef long _copy_list_composite(SrcBuffer src, long p, long src_pos,
                               SegmentBuilder dst, long dst_pos) except -1:
    src_pos = ptr.deref(p, src_pos)
    cdef long total_words = ptr.list_item_count(p) # n of words NOT including the tag
    cdef long body_length = (total_words+1)*8      # total length INCLUDING the tag
    #
    # check that there is enough data for both the tag AND the whole body;
    # this way we do the bound checking only once
    check_bound(src_pos, body_length, src.len)
    cdef long tag = read_int64(src, src_pos)
    cdef long count = ptr.offset(tag)
    cdef long data_size = ptr.struct_data_size(tag)
    cdef long ptrs_size = ptr.struct_ptrs_size(tag)
    #
    # allocate the list and copy the whole body at once
    dst_pos = dst.alloc_list(dst_pos, ptr.LIST_SIZE_COMPOSITE, total_words, body_length)
    dst.memcpy_from(dst_pos, src.cbuf+src_pos, body_length)
    #
    # iterate over the elements, fix the pointers and copy the content
    cdef long i = 0
    cdef long item_length = (data_size+ptrs_size) * 8
    cdef long ptrs_section_offset = 0
    for i in range(count):
        ptrs_section_offset = 8 + item_length*i + data_size*8
        _copy_many_ptrs(ptrs_size, src,
                        src_pos + ptrs_section_offset,
                        dst,
                        dst_pos + ptrs_section_offset)
