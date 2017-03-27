cimport cython
from libc.stdint cimport (int8_t, uint8_t, int16_t, uint16_t,
                          uint32_t, int32_t, int64_t, uint64_t)


@cython.final
cdef class MutableBuffer(object):
    cdef bytearray buf
    cdef char* cbuf
    cdef readonly long length  # length of the allocated buffer
    cdef readonly long end     # index of the current end position of cbuf;
                               # the next allocation will start at this
                               # position

    cdef void _resize(self, Py_ssize_t minlen)
    cpdef as_string(self)
    cpdef void set_int64(self, long i, int64_t value)
    cdef void memcpy_from(self, long i, const char* src, long n)
    cpdef long allocate(self, long length)
    cpdef long alloc_struct(self, long pos, long data_size, long ptrs_size)
    cpdef long alloc_list(self, long pos, long size_tag, long item_count,
                          long body_length)
