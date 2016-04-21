import cython
from capnpy.filelike cimport FileLike

cdef class BufferedSocket(FileLike):
    cdef readonly object sock
    cdef readonly int bufsize
    cdef readonly bytes buf
    cdef readonly int i

    cdef _fillbuf(self, int size)
    cdef _readall(self)


cdef class StringBuffer(FileLike):
    cdef readonly bytes s
    cdef readonly int i

    @cython.locals(i=int, j=int)
    cpdef bytes read(self, int size=*)

    @cython.locals(i=int, j=int)
    cpdef bytes readline(self)
