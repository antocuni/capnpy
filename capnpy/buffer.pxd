cimport cython
from libc.stdint cimport (int8_t, uint8_t, int16_t, uint16_t,
                          uint32_t, int32_t, int64_t, uint64_t)


@cython.final
cdef class MutableBuffer(object):
    cdef bytearray buf
    cdef char* cbuf
    cdef readonly Py_ssize_t length  # length of the allocated buffer
    cdef readonly Py_ssize_t end     # index of the current end position of
                                     # cbuf; the next allocation will start at
                                     # this position

    cdef void _resize(self, Py_ssize_t minlen)
    cpdef as_string(self)
    cpdef void write_int64(self, Py_ssize_t i, int64_t value)
    cdef void memcpy_from(self, Py_ssize_t i, const char* src, Py_ssize_t n)
    cpdef Py_ssize_t allocate(self, Py_ssize_t length)
    cpdef Py_ssize_t alloc_struct(self, Py_ssize_t pos, long data_size, long ptrs_size)
    cpdef Py_ssize_t alloc_list(self, Py_ssize_t pos, long size_tag, long item_count,
                                long body_length)
