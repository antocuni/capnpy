cdef class BuiltinType:
    cdef readonly str name
    cdef readonly bytes fmt
    cdef readonly char ifmt
