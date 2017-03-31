cimport cython
from libc.stdint cimport (int8_t, uint8_t, int16_t, uint16_t,
                          uint32_t, int32_t, int64_t, uint64_t)
from capnpy cimport ptr


@cython.final
cdef class SegmentBuilder(object):
    cdef bytearray buf
    cdef char* cbuf
    cdef readonly Py_ssize_t length  # length of the allocated buffer
    cdef readonly Py_ssize_t end     # index of the current end position of
                                     # cbuf; the next allocation will start at
                                     # this position

    cdef void _resize(self, Py_ssize_t minlen)
    cpdef as_string(self)

    cpdef void write_int8(self, Py_ssize_t i, int8_t value)
    cpdef void write_uint8(self, Py_ssize_t i, uint8_t value)
    cpdef void write_int16(self, Py_ssize_t i, int16_t value)
    cpdef void write_uint16(self, Py_ssize_t i, uint16_t value)
    cpdef void write_int32(self, Py_ssize_t i, int32_t value)
    cpdef void write_uint32(self, Py_ssize_t i, uint32_t value)
    cpdef void write_int64(self, Py_ssize_t i, int64_t value)
    cpdef void write_uint64(self, Py_ssize_t i, uint64_t value)
    cpdef void write_float(self, Py_ssize_t i, float value)
    cpdef void write_double(self, Py_ssize_t i, double value)

    cdef void memcpy_from(self, Py_ssize_t i, const char* src, Py_ssize_t n)
    cpdef Py_ssize_t allocate(self, Py_ssize_t length)
    cpdef Py_ssize_t alloc_struct(self, Py_ssize_t pos, long data_size, long ptrs_size)
    cpdef Py_ssize_t alloc_list(self, Py_ssize_t pos, long size_tag, long item_count,
                                long body_length)
    cpdef Py_ssize_t alloc_text(self, Py_ssize_t pos, bytes s, long trailing_zero=*)
    cpdef Py_ssize_t alloc_data(self, Py_ssize_t pos, bytes s)



