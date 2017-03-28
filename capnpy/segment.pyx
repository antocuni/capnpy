from libc.stdint cimport (int8_t, uint8_t, int16_t, uint16_t,
                          uint32_t, int32_t, int64_t, uint64_t, INT64_MAX)
from libc.string cimport memcpy, memset
from cpython.string cimport (PyString_AS_STRING, PyString_GET_SIZE,
                             PyString_FromStringAndSize)
from capnpy cimport ptr

cdef extern from "Python.h":
    int PyByteArray_Resize(object o, Py_ssize_t len)
    char* PyByteArray_AS_STRING(object o)

cdef long round_to_word(long pos):
    return (pos + (8 - 1)) & -8  # Round up to 8-byte boundary


cimport cython
@cython.final
cdef class Segment(object):
    cdef bytes buf
    cdef const char* cbuf

    def __cinit__(self, bytes buf):
        self.buf = buf
        self.cbuf = PyString_AS_STRING(self.buf)

    cdef inline check_bounds(self, Py_ssize_t size, Py_ssize_t offset):
        # the bound check seems to introduce a 5-10% overhead when calling
        # read_int64 from Python. However, I expect the overhead to be
        # relatively much higher if you call it from C. In case it's needed,
        # consider adding a read_int64_fast or similar method, which does
        # *not* do the check.
        cdef Py_ssize_t buflen = PyString_GET_SIZE(self.buf)
        if offset < 0 or offset + size > buflen:
            raise IndexError('Offset out of bounds: %d' % offset)

    cpdef int64_t read_int64(self, Py_ssize_t offset) except? -1:
        self.check_bounds(8, offset)
        return (<int64_t*>(self.cbuf+offset))[0]

    cpdef uint64_t read_uint64(self, Py_ssize_t offset) except? -1:
        # if the value is small enough, it returns a python int. Else, a
        # python long
        self.check_bounds(8, offset)
        uint64_value = (<uint64_t*>self.cbuf)[0]
        if uint64_value <= INT64_MAX:
            return <int64_t>uint64_value
        else:
            return uint64_value

    cpdef int32_t read_int32(self, Py_ssize_t offset) except? -1:
        self.check_bounds(4, offset)
        return (<int32_t*>self.cbuf)[0]

    cpdef uint32_t read_uint32(self, Py_ssize_t offset) except? -1:
        self.check_bounds(4, offset)
        return (<uint32_t*>self.cbuf)[0]

    cpdef int16_t read_int16(self, Py_ssize_t offset) except? -1:
        self.check_bounds(2, offset)
        return (<int16_t*>self.cbuf)[0]

    cpdef uint16_t read_uint16(self, Py_ssize_t offset) except? -1:
        self.check_bounds(2, offset)
        return (<uint16_t*>self.cbuf)[0]

    cpdef int8_t read_int8(self, Py_ssize_t offset) except? -1:
        self.check_bounds(1, offset)
        return (<int8_t*>self.cbuf)[0]

    cpdef uint8_t read_uint8(self, Py_ssize_t offset) except? -1:
        self.check_bounds(1, offset)
        return (<uint8_t*>self.cbuf)[0]

    cpdef double read_double(self, Py_ssize_t offset) except? -1:
        self.check_bounds(8, offset)
        return (<double*>self.cbuf)[0]

    cpdef float read_float(self, Py_ssize_t offset) except? -1:
        self.check_bounds(4, offset)
        return (<float*>self.cbuf)[0]



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

    cpdef void write_int64(self, Py_ssize_t i, int64_t value):
        (<int64_t*>(self.cbuf+i))[0] = value

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


