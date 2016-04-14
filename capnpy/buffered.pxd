cdef class BufferedSocket:
    cdef readonly object sock
    cdef readonly int bufsize
    cdef readonly str buf
    cdef readonly int i

    cdef _fillbuf(self, int size)
    cpdef str read(self, int size)
    cpdef str readline(self)
