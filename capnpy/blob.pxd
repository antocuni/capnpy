from capnpy.type cimport BuiltinType
from capnpy.unpack cimport unpack_primitive

cdef class CapnpBuffer:
    cdef readonly bytes s
    cdef readonly object segment_offsets

cdef class Blob:
    cdef readonly CapnpBuffer _buf

    
