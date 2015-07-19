cdef class Primitive:
    cdef readonly object name
    cdef readonly long offset
    cdef readonly object type
    cdef readonly object default_
    cdef readonly str fmt
