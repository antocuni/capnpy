import cython
from capnpy.type cimport BuiltinType
from capnpy.unpack cimport unpack_primitive, unpack_int64, unpack_int16
from capnpy cimport ptr
from capnpy cimport _hash

cdef enum:
    E_IS_FAR_POINTER = -1

cdef class CapnpBuffer:
    cdef readonly bytes s
    cpdef read_primitive(self, long offset, char ifmt)
    cpdef long read_int16(self, long offset)
    cpdef long read_raw_ptr(self, long offset)
    cpdef long read_ptr(self, long offset)
    cpdef read_far_ptr(self, long offset)

    @cython.locals(p=long, start=long, end=long)
    cpdef read_str(self, long p, long offset, default_, int additional_size)

    @cython.locals(p=long, start=long, size=long)
    cpdef long hash_str(self, long p, long offset, long default_, int additional_size)

    
cdef class CapnpBufferWithSegments(CapnpBuffer):
    cdef readonly object segment_offsets

cdef class Blob:
    cdef readonly CapnpBuffer _buf

    cpdef _init_blob(self, object buf)
    cpdef _read_ptr_generic(self, long offset)
