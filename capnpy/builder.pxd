import cython
from capnpy cimport ptr
from capnpy.packing cimport pack_into, pack_int64_into
from capnpy.list cimport List, ItemType


cdef class AbstractBuilder(object):
    cdef public long _length
    cdef public list _extra
    cdef public long _total_length

    cdef long _calc_relative_offset(self, long offset)
    cpdef _alloc(self, bytes s)
    cdef _record_allocation(self, long offset, long p)

    @cython.locals(padding=long)
    cdef _force_alignment(self)

    @cython.locals(ptr_offset=long, p=long)
    cpdef alloc_data(self, int offset, bytes value, bytes suffix=*)

    cpdef alloc_text(self, int offset, bytes value)

cdef class Builder(AbstractBuilder):
    cdef public bytearray _buf
    cpdef set(self, char ifmt, int offset, object value)
    cpdef bytes build(self)


cdef class ListBuilder(AbstractBuilder):
    cdef public ItemType item_type
    cdef public long item_length
    cdef public long size_tag
    cdef public long item_count
    cdef public object _items
