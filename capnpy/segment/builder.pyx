cimport cython
from libc.stdint cimport (int8_t, uint8_t, int16_t, uint16_t,
                          uint32_t, int32_t, int64_t, uint64_t, INT64_MAX)
from libc.string cimport memcpy, memset
from cpython.string cimport (PyString_FromStringAndSize, PyString_GET_SIZE,
                             PyString_AS_STRING)

cdef extern from "Python.h":
    int PyByteArray_Resize(object o, Py_ssize_t len)
    char* PyByteArray_AS_STRING(object o)

cdef long round_to_word(long pos):
    return (pos + (8 - 1)) & -8  # Round up to 8-byte boundary


cdef class SegmentBuilder(object):

    def __cinit__(self, long length=512):
        self.length = length
        self.buf = bytearray(self.length)
        self.cbuf = PyByteArray_AS_STRING(self.buf)
        self.end = 0

    cdef void _resize(self, Py_ssize_t minlen):
        # exponential growth of the buffer. By using this formula, we grow
        # faster at the beginning (where the constant plays a major role) and
        # slower when the buffer it's already big (where length >> 1 plays a
        # major role)
        cdef long newlen = self.length + ( self.length >> 1 ) + 512;
        newlen = max(minlen, newlen)
        newlen = round_to_word(newlen)
        cdef long curlen = self.length
        PyByteArray_Resize(self.buf, newlen)
        cdef char* oldbuf = self.cbuf
        self.cbuf = PyByteArray_AS_STRING(self.buf)
        ## if oldbuf != self.cbuf:
        ##     print 'REALLOC %s --> %s' % (curlen, newlen)
        ## else:
        ##     print '        %s --> %s' % (curlen, newlen)
        memset(self.cbuf + curlen, 0, newlen - curlen)
        self.length = newlen

    cpdef as_string(self):
        return PyString_FromStringAndSize(self.cbuf, self.end)

    cpdef void write_int8(self, Py_ssize_t i, int8_t value):
        (<int8_t*>(self.cbuf+i))[0] = value

    cpdef void write_uint8(self, Py_ssize_t i, uint8_t value):
        (<uint8_t*>(self.cbuf+i))[0] = value

    cpdef void write_int16(self, Py_ssize_t i, int16_t value):
        (<int16_t*>(self.cbuf+i))[0] = value

    cpdef void write_uint16(self, Py_ssize_t i, uint16_t value):
        (<uint16_t*>(self.cbuf+i))[0] = value

    cpdef void write_int32(self, Py_ssize_t i, int32_t value):
        (<int32_t*>(self.cbuf+i))[0] = value

    cpdef void write_uint32(self, Py_ssize_t i, uint32_t value):
        (<uint32_t*>(self.cbuf+i))[0] = value

    cpdef void write_int64(self, Py_ssize_t i, int64_t value):
        (<int64_t*>(self.cbuf+i))[0] = value

    cpdef void write_uint64(self, Py_ssize_t i, uint64_t value):
        (<uint64_t*>(self.cbuf+i))[0] = value

    cpdef void write_float(self, Py_ssize_t i, float value):
        (<float*>(self.cbuf+i))[0] = value

    cpdef void write_double(self, Py_ssize_t i, double value):
        (<double*>(self.cbuf+i))[0] = value

    cdef void memcpy_from(self, Py_ssize_t i, const char* src, Py_ssize_t n):
        cdef void* dst = self.cbuf + i
        memcpy(dst, src, n)

    cpdef Py_ssize_t allocate(self, Py_ssize_t length):
        """
        Allocate ``length`` bytes of memory inside the buffer. Return the start
        position of the newly allocated space.
        """
        cdef Py_ssize_t result = self.end
        self.end += length
        if self.end > self.length:
            self._resize(self.end)
        return result

    cpdef Py_ssize_t alloc_struct(self, Py_ssize_t pos, long data_size, long ptrs_size):
        """
        Allocate a new struct of the given size, and write the resulting pointer
        at position i. Return the newly allocated position.
        """
        cdef long length = (data_size+ptrs_size) * 8
        cdef Py_ssize_t result = self.allocate(length)
        cdef long offet = result - (pos+8)
        cdef long p = ptr.new_struct(offet/8, data_size, ptrs_size)
        self.write_int64(pos, p)
        return result

    cpdef Py_ssize_t alloc_list(self, Py_ssize_t pos, long size_tag, long item_count,
                                long body_length):
        """
        Allocate a new list of the given size, and write the resulting pointer
        at position i. Return the newly allocated position.
        """
        body_length = round_to_word(body_length)
        cdef Py_ssize_t result = self.allocate(body_length)
        cdef long offet = result - (pos+8)
        cdef long p = ptr.new_list(offet/8, size_tag, item_count)
        self.write_int64(pos, p)
        return result

    cpdef Py_ssize_t alloc_text(self, Py_ssize_t pos, bytes s, long trailing_zero=1):
        if s is None:
            self.write_int64(pos, 0)
            return -1
        cdef Py_ssize_t n = PyString_GET_SIZE(s)
        cdef Py_ssize_t nn = n + trailing_zero
        cdef const char *src = PyString_AS_STRING(s)
        cdef Py_ssize_t result = self.alloc_list(pos, ptr.LIST_SIZE_8, nn, nn)
        self.memcpy_from(result, src, n)
        # there is no need to write the trailing 0 as the byte is already
        # guaranteed to be 0
        return result

    cpdef Py_ssize_t alloc_data(self, Py_ssize_t pos, bytes s):
        return self.alloc_text(pos, s, trailing_zero=0)
