import cython
from capnpy.type cimport BuiltinType
from capnpy.packing cimport unpack_primitive, unpack_int64, unpack_int16
from capnpy cimport ptr
from capnpy cimport _hash
from capnpy.segment.segment cimport Segment

cdef class Blob:
    cdef readonly Segment _seg

    cpdef _init_blob(self, object buf)
    cpdef _richcmp(self, other, int op)
