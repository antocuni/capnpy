from capnpy.blob cimport Blob

cdef class Struct(Blob):
    cdef public long _data_offset
    cdef public long _ptrs_offset
    cdef public long _data_size
    cdef public long _ptrs_size
