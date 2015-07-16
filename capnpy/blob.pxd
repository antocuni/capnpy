cdef class Blob:
    cdef readonly object _buf
    cdef readonly long _offset
    cdef readonly object _segment_offsets
