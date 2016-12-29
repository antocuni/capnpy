import cython
from capnpy.blob cimport Blob
from capnpy cimport ptr

cdef class List(Blob):
    cdef public long _offset
    cdef public object _item_type
    cdef public long _ptrs_size
    cdef public long _size_tag
    cdef public long _item_count
    cdef public long _item_length

    cpdef _init_from_buffer(self, object buf, long offset, long size_tag,
                            long item_count, object item_type)
    cpdef _set_list_tag(self, long size_tag, long item_count)
    cpdef long _get_offset_for_item(self, long i)
    # XXX __getitem__ ?
    # XXX _read_list_item
    cpdef _getitem_fast(self, long i)
