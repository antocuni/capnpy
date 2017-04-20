cimport cython
from libc.stdint cimport (int8_t, uint8_t, int16_t, uint16_t,
                          uint32_t, int32_t, int64_t, uint64_t)
from capnpy cimport ptr
from capnpy.segment.base cimport BaseSegment
from capnpy.struct_ cimport Struct

@cython.final
cdef class SegmentBuilder(object):
    cdef bytearray buf
    cdef char* cbuf
    cdef readonly Py_ssize_t length  # length of the allocated buffer
    cdef readonly Py_ssize_t end     # index of the current end position of
                                     # cbuf; the next allocation will start at
                                     # this position

    cdef void _resize(self, Py_ssize_t minlen)
    cpdef Py_ssize_t get_length(self)
    cpdef as_string(self)

    cpdef object write_generic(self, char ifmt, Py_ssize_t i, object value)
    cpdef void write_int8(self, Py_ssize_t i, int8_t value)
    cpdef void write_uint8(self, Py_ssize_t i, uint8_t value)
    cpdef void write_int16(self, Py_ssize_t i, int16_t value)
    cpdef void write_uint16(self, Py_ssize_t i, uint16_t value)
    cpdef void write_int32(self, Py_ssize_t i, int32_t value)
    cpdef void write_uint32(self, Py_ssize_t i, uint32_t value)
    cpdef void write_int64(self, Py_ssize_t i, int64_t value)
    cpdef void write_uint64(self, Py_ssize_t i, uint64_t value)
    cpdef void write_float32(self, Py_ssize_t i, float value)
    cpdef void write_float64(self, Py_ssize_t i, double value)
    cpdef void write_bool(self, Py_ssize_t byteoffset, int bitoffset, bint value)
    cpdef void write_slice(self, Py_ssize_t i, BaseSegment src, Py_ssize_t start, Py_ssize_t n)

    cpdef Py_ssize_t allocate(self, Py_ssize_t length)
    cpdef Py_ssize_t alloc_struct(self, Py_ssize_t pos, long data_size, long ptrs_size)
    cpdef Py_ssize_t alloc_list(self, Py_ssize_t pos, long size_tag, long item_count,
                                long body_length)
    cpdef Py_ssize_t alloc_text(self, Py_ssize_t pos, bytes s, long trailing_zero=*)
    cpdef Py_ssize_t alloc_data(self, Py_ssize_t pos, bytes s)
    cpdef copy_from_pointer(self, Py_ssize_t dst_pos, BaseSegment src, long p,
                            Py_ssize_t src_pos)
    cpdef copy_from_struct(self, Py_ssize_t dst_pos, type structcls, Struct value)
    cpdef copy_inline_struct(self, Py_ssize_t dst_pos, BaseSegment src,
                             long p, Py_ssize_t src_pos)
    cpdef copy_from_list(self, Py_ssize_t pos, item_type, lst)
