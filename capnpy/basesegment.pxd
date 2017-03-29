cimport cython
from libc.stdint cimport (int8_t, uint8_t, int16_t, uint16_t,
                          uint32_t, int32_t, int64_t, uint64_t)


cdef class BaseSegment(object):
    cdef readonly bytes buf
    cdef const char* cbuf

    cdef inline check_bounds(self, Py_ssize_t size, Py_ssize_t offset)
    cdef object read_primitive(self, Py_ssize_t offset, char ifmt)
    cdef int64_t read_int64(self, Py_ssize_t offset) except? 0x7fffffffffffffff
    cdef uint64_t read_uint64(self, Py_ssize_t offset) except? 0xffffffffffffffff
    cdef object read_uint64_magic(self, Py_ssize_t offset)
    cdef int32_t read_int32(self, Py_ssize_t offset) except? 0x7fffffff
    cdef uint32_t read_uint32(self, Py_ssize_t offset) except? 0xffffffff
    cdef int16_t read_int16(self, Py_ssize_t offset) except? 0x7fff
    cdef uint16_t read_uint16(self, Py_ssize_t offset) except? 0xffff
    cdef int8_t read_int8(self, Py_ssize_t offset) except? 0x7f
    cdef uint8_t read_uint8(self, Py_ssize_t offset) except? 0xff
    cdef double read_double(self, Py_ssize_t offset) except? -1
    cdef float read_float(self, Py_ssize_t offset) except? -1


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
    cpdef void write_int64(self, Py_ssize_t i, int64_t value)
    cdef void memcpy_from(self, Py_ssize_t i, const char* src, Py_ssize_t n)
    cpdef Py_ssize_t allocate(self, Py_ssize_t length)
    cpdef Py_ssize_t alloc_struct(self, Py_ssize_t pos, long data_size, long ptrs_size)
    cpdef Py_ssize_t alloc_list(self, Py_ssize_t pos, long size_tag, long item_count,
                                long body_length)
