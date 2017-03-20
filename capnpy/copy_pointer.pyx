cimport cython
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

    def __cinit__(self):
        cdef Py_ssize_t unused
        self.length = 4096 # XXX: don't use a fixed size
        self.buf = bytearray(self.length)
        self.cbuf = as_cbuf(self.buf, &unused)
        self.end = 0

    cpdef char* allocate(self, long length):
        cdef long end = self.end
        self.end += length
        return self.cbuf + end

    cpdef as_bytes(self):
        return PyString_FromStringAndSize(self.cbuf, self.end)
