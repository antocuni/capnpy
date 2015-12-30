from capnpy.blob cimport Blob

cdef class Struct(Blob):
    cdef public long __data_size__
    cdef public long __ptrs_size__

