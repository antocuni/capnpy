cimport cython
from libc.stdint cimport (int8_t, uint8_t, int16_t, uint16_t,
                          uint32_t, int32_t, int64_t, uint64_t)
from libc.string cimport memcpy
from cpython.string cimport PyString_AS_STRING, PyString_FromStringAndSize
from capnpy cimport ptr
from capnpy.packing cimport as_cbuf

cdef extern from "Python.h":
    char* PyByteArray_AS_STRING(object o)


@cython.final
cdef class MutableBuffer(object):
    cdef bytearray buf
    cdef char* cbuf
    cdef long length
    cdef long end # index of the current end position of cbuf; the next
                  # allocation will start at this position

    def __cinit__(self, length):
        cdef Py_ssize_t unused
        self.length = length
        self.buf = bytearray(self.length)
        self.cbuf = as_cbuf(self.buf, &unused)
        self.end = 0

    cpdef as_string(self):
        return PyString_FromStringAndSize(self.cbuf, self.end)

    cpdef void set_int64(self, long i, int64_t value):
        (<int64_t*>(self.cbuf+i))[0] = value

    cdef void memcpy_from(self, long i, const char* src, long n):
        cdef void* dst = self.cbuf + i
        memcpy(dst, src, n)

    cpdef long allocate(self, long length) except -1:
        """
        Allocate ``length`` bytes of memory inside the buffer. Return the start
        position of the newly allocated space.
        """
        cdef long result = self.end
        self.end += length
        if self.end > self.length:
            raise ValueError("buffer too small; TODO: implement resizing or multiple segments")
        return result

    cpdef long alloc_struct(self, long pos, long data_size, long ptrs_size) except -1:
        """
        Allocate a new struct of the given size, and write the resulting pointer
        at position i. Return the newly allocated position.
        """
        cdef long length = (data_size+ptrs_size) * 8
        cdef long result = self.allocate(length)
        cdef long offet = result - (pos+8)
        cdef long p = ptr.new_struct(offet/8, data_size, ptrs_size)
        self.set_int64(pos, p)
        return result

    cpdef long alloc_list(self, long pos, long size_tag, long item_count,
                          long body_length) except -1:
        """
        Allocate a new list of the given size, and write the resulting pointer
        at position i. Return the newly allocated position.
        """
        body_length = round_to_word(body_length)
        cdef long result = self.allocate(body_length)
        cdef long offet = result - (pos+8)
        cdef long p = ptr.new_list(offet/8, size_tag, item_count)
        self.set_int64(pos, p)
        return result

cdef long round_to_word(long pos):
    return (pos + (8 - 1)) & -8;  # Round up to 8-byte boundary


cdef int64_t read_int64(const char* src, long i):
    return (<int64_t*>(src+i))[0]

cpdef copy_pointer(bytes src, long p, long src_pos, MutableBuffer dst, long dst_pos):
    """
    Copy from: buffer src, pointer p living at the src_pos offset
         to:   buffer dst at position dst_pos
    """
    cdef Py_ssize_t src_len
    cdef char* srcbuf = as_cbuf(src, &src_len)
    _copy(srcbuf, src_len, p, src_pos, dst, dst_pos)


cdef long _copy(const char* src, Py_ssize_t src_len, long p, long src_pos,
                MutableBuffer dst, long dst_pos) except -1:
    cdef long kind = ptr.kind(p)
    if kind == ptr.STRUCT:
        return _copy_struct(src, src_len, p, src_pos, dst, dst_pos)
    elif kind == ptr.LIST:
        item_size = ptr.list_size_tag(p)
        if item_size == ptr.LIST_SIZE_COMPOSITE:
            return _copy_list_composite(src, src_len, p, src_pos, dst, dst_pos)
        elif item_size == ptr.LIST_SIZE_PTR:
            return _copy_list_ptr(src, src_len, p, src_pos, dst, dst_pos)
        else:
            return _copy_list_primitive(src, src_len, p, src_pos, dst, dst_pos)
    ## elif kind == ptr.FAR:
    ##     raise NotImplementedError('Far pointer not supported')
    assert False, 'unknown ptr kind: %s' % kind

cdef long _copy_many_ptrs(long n, const char* src, Py_ssize_t src_len, long src_pos,
                          MutableBuffer dst, long dst_pos) except -1:
    cdef long i, p, offset
    check_bound(src_pos, n*8, src_len)
    for i in range(n):
        offset = i*8
        p = read_int64(src, src_pos + offset)
        if p != 0:
            _copy(src, src_len, p, src_pos + offset, dst, dst_pos + offset)

cdef long check_bound(long pos, long n, Py_ssize_t src_len) except -1:
    if pos+n > src_len:
        msg = ("Invalid capnproto message: offset out of bound "
               "at position %s (%s > %s)" % (pos, pos+n, src_len))
        raise IndexError(msg)

cdef long _copy_struct(const char* src, Py_ssize_t src_len, long p, long src_pos,
                       MutableBuffer dst, long dst_pos) except -1:
    src_pos = ptr.deref(p, src_pos)
    cdef long data_size = ptr.struct_data_size(p)
    cdef long ptrs_size = ptr.struct_ptrs_size(p)
    cdef long ds = data_size*8
    dst_pos = dst.alloc_struct(dst_pos, data_size, ptrs_size)
    check_bound(src_pos, ds, src_len)
    dst.memcpy_from(dst_pos, src+src_pos, ds) # copy data section
    _copy_many_ptrs(ptrs_size, src, src_len, src_pos+ds, dst, dst_pos+ds)


cdef long _copy_list_primitive(const char* src, Py_ssize_t src_len, long p, long src_pos,
                               MutableBuffer dst, long dst_pos) except -1:
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
    check_bound(src_pos, body_length, src_len)
    dst.memcpy_from(dst_pos, src+src_pos, body_length)

cdef long _copy_list_ptr(const char* src, Py_ssize_t src_len, long p, long src_pos,
                         MutableBuffer dst, long dst_pos) except -1:
    src_pos = ptr.deref(p, src_pos)
    cdef long count = ptr.list_item_count(p)
    cdef long body_length = count*8
    dst_pos = dst.alloc_list(dst_pos, ptr.LIST_SIZE_PTR, count, body_length)
    check_bound(src_pos, body_length, src_len)
    _copy_many_ptrs(count, src, src_len, src_pos, dst, dst_pos)


cdef long _copy_list_composite(const char* src, Py_ssize_t src_len, long p, long src_pos,
                               MutableBuffer dst, long dst_pos) except -1:
    src_pos = ptr.deref(p, src_pos)
    cdef long total_words = ptr.list_item_count(p) # n of words NOT including the tag
    cdef long body_length = (total_words+1)*8      # total length INCLUDING the tag
    #
    # check that there is enough data for both the tag AND the whole body;
    # this way we do the bound checking only once
    check_bound(src_pos, body_length, src_len)
    cdef long tag = read_int64(src, src_pos)
    cdef long count = ptr.offset(tag)
    cdef long data_size = ptr.struct_data_size(tag)
    cdef long ptrs_size = ptr.struct_ptrs_size(tag)
    #
    # allocate the list and copy the whole body at once
    dst_pos = dst.alloc_list(dst_pos, ptr.LIST_SIZE_COMPOSITE, total_words, body_length)
    dst.memcpy_from(dst_pos, src+src_pos, body_length)
    #
    # iterate over the elements, fix the pointers and copy the content
    cdef long i = 0
    cdef long item_length = (data_size+ptrs_size) * 8
    cdef long ptrs_section_offset = 0
    for i in range(count):
        ptrs_section_offset = 8 + item_length*i + data_size*8
        _copy_many_ptrs(ptrs_size, src, src_len,
                        src_pos + ptrs_section_offset,
                        dst,
                        dst_pos + ptrs_section_offset)
