import cython
from capnpy.filelike cimport FileLike

cdef class BufferedStream(FileLike):
    cdef readonly bytes buf
    cdef readonly int i

    cdef _fillbuf(self, int size)
    cdef bytes _readall(self)
    cpdef bytes _readchunk(self)

    @cython.locals(i=int, j=int)
    cpdef bytes read(self, int size=*)

    @cython.locals(i=int, j=int)
    cpdef bytes readline(self)


cdef class BufferedSocket(BufferedStream):
    cdef readonly object sock
    cdef readonly int bufsize
    cdef public object wbuf
    cpdef bytes _readchunk(self)


cdef class StringBuffer(FileLike):
    cdef readonly bytes s
    cdef readonly int i

    @cython.locals(i=int, j=int)
    cpdef bytes read(self, int size=*)

    @cython.locals(i=int, j=int)
    cpdef bytes readline(self)

    cpdef int tell(self)
