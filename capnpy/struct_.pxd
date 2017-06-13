import cython
from capnpy.blob cimport Blob
from capnpy.visit cimport end_of
from capnpy cimport ptr
from capnpy.list cimport List, ItemType
from capnpy.packing cimport pack_int64
from capnpy.segment.builder cimport SegmentBuilder

cpdef str check_tag(str curtag, str newtag)


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
    cpdef long _read_data_int16(self, long offset)
    cpdef long _read_fast_ptr(self, long offset)
    cpdef _read_far_ptr(self, long offset)
    cpdef long _as_pointer(self, long offset)

    @cython.locals(p=long, obj=Struct)
    cpdef _read_struct(self, long offset, type structcls)

    @cython.locals(p=long, offset=long)
    cpdef _read_str_text(self, long offset, str default_=*)

    @cython.locals(p=long, offset=long)
    cpdef _read_str_data(self, long offset, str default_=*, int additional_size=*)

    @cython.locals(p=long, offset=long, obj=List)
    cpdef _read_list(self, long offset, ItemType item_type, default_=*)

    @cython.locals(p=long, offset=long)
    cpdef long _hash_str_text(self, long offset, long default_=*)

    @cython.locals(p=long, offset=long)
    cpdef long _hash_str_data(self, long offset, long default_=*, int additional_size=*)

    cpdef object _ensure_union(self, long expected_tag)
    cpdef long __which__(self) except -1

    cpdef long _get_end(self)
    cpdef long _is_compact(self)

    @cython.locals(builder=SegmentBuilder, pos=long, buf=bytes, t=type, res=Struct)
    cpdef object compact(self)
    
