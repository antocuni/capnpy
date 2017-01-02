cdef class BuiltinType:
    cdef readonly bytes name
    cdef readonly bytes fmt
    cdef readonly char ifmt
    cdef public object list_item_type # XXX the type should be BuiltinType
