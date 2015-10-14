from capnpy.type cimport BuiltinType
cimport capnpy.unpack

cdef class Blob:
    cdef readonly bytes _buf
    cdef readonly long _offset
    cdef readonly object _segment_offsets
    cpdef _read_primitive(self, int offset, BuiltinType t)
