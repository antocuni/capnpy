import cython
from capnpy.blob cimport Blob
from capnpy cimport ptr

cpdef assert_undefined(object val, str name, str other_name)


@cython.locals(self=Struct)
cpdef struct_from_buffer(type cls, object buf, long offset,
                         long data_size, long ptrs_size)


cdef class Struct(Blob):
    cdef public long _data_offset
    cdef public long _ptrs_offset
    cdef public long _data_size
    cdef public long _ptrs_size

    cpdef _init_from_buffer(self, object buf, long offset,
                            long data_size, long ptrs_size)
    cpdef _init_from_pointer(self, object buf, long offset, long p)
    cpdef _read_data(self, long offset, char ifmt)
    cpdef _read_ptr(self, long offset)
    cpdef long _read_raw_ptr(self, long offset)

    cpdef object _ensure_union(self, long expected_tag)
    cpdef long __which__(self) except -1
