from capnpy.filelike cimport FileLike

cdef class BufferedSocket(FileLike):
    cdef readonly object sock
    cdef readonly int bufsize
    cdef readonly bytes buf
    cdef readonly int i

    cdef _fillbuf(self, int size)
