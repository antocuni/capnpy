cpdef FileLike as_filelike(object f)

cdef class FileLike:
    cpdef bytes read(self, int size=*)
    cpdef bytes readline(self)

cdef class FileLikeAdapter(FileLike):
    cdef object _read
    cdef object _readline

    cpdef bytes read(self, int size=*)
    cpdef bytes readline(self)
