cdef class BufferedSocket:
    cdef readonly object sock
    cdef readonly int bufsize
    cdef readonly bytes buf
    cdef readonly int i

    cdef _fillbuf(self, int size)
    cpdef bytes read(self, int size)
    cpdef bytes readline(self)
