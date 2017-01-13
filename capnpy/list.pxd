import cython
from capnpy.blob cimport Blob
from capnpy.type cimport BuiltinType
from capnpy cimport ptr

cdef class ItemType(object)

cdef class List(Blob):
    cdef readonly long _offset
    cdef readonly ItemType _item_type
    cdef readonly long _ptrs_size
    cdef readonly long _size_tag
    cdef readonly long _tag
    cdef readonly long _item_count
    cdef readonly long _item_length
    cdef readonly long _item_offset

    cpdef _init_from_buffer(self, object buf, long offset, long size_tag,
                            long item_count, ItemType item_type)
    cpdef _set_list_tag(self, long size_tag, long item_count)
    cpdef long _get_offset_for_item(self, long i)
    cpdef _getitem_fast(self, long i)

cdef class ItemType(object):
    cpdef read_item(self, List lst, long offset)
    cpdef bint can_compare(self)

cdef class VoidItemType(ItemType):
    pass

cdef class BoolItemType(ItemType):
    pass

cdef class PrimitiveItemType(ItemType):
    cdef readonly BuiltinType t
    cdef readonly char ifmt

cdef class EnumItemType(PrimitiveItemType):
    cdef readonly object enumcls

cdef class StructItemType(ItemType):
    cdef readonly object structcls

cdef class TextItemType(ItemType):
    pass


cpdef ItemType void_list_item_type
cpdef ItemType bool_list_item_type
cpdef ItemType int8_list_item_type
cpdef ItemType uint8_list_item_type
cpdef ItemType int16_list_item_type
cpdef ItemType uint16_list_item_type
cpdef ItemType int32_list_item_type
cpdef ItemType uint32_list_item_type
cpdef ItemType int64_list_item_type
cpdef ItemType uint64_list_item_type
cpdef ItemType float32_list_item_type
cpdef ItemType float64_list_item_type
cpdef ItemType text_list_item_type
cpdef ItemType data_list_item_type
