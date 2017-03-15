from capnpy.list cimport List, ItemType

cdef class AbstractBuilder(object):
    cdef public long _length
    cdef public object _extra
    cdef public long _total_length

cdef class Builder(AbstractBuilder):
    cdef public bytearray _buf

cdef class ListBuilder(AbstractBuilder):
    cdef public ItemType item_type
    cdef public long item_length
    cdef public long size_tag
    cdef public long item_count
    cdef public object _items
