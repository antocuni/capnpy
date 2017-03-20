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

    cpdef as_bytes(self):
        return PyString_FromStringAndSize(self.cbuf, self.end)

    cpdef void set_int64(self, long i, int64_t value):
        (<int64_t*>(self.cbuf+i))[0] = value

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

    cpdef long new_struct(self, long i, long data_size, long ptrs_size) except -1:
        """
        Allocate a new struct of the given size, and write the resulting pointer
        at position i. Return the newly allocated position.
        """
        cdef long length = (data_size+ptrs_size) * 8
        cdef long result = self.allocate(length)
        cdef long offet = result - (i+8)
        cdef long p = ptr.new_struct(offet/8, data_size, ptrs_size)
        self.set_int64(i, p)
        return result
