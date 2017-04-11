import cython
from capnpy.blob cimport Blob
from capnpy.struct_ cimport Struct
from capnpy.type cimport BuiltinType
from capnpy cimport ptr
from capnpy.visit cimport end_of
from capnpy.segment.builder cimport SegmentBuilder

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
    cpdef _getitem_fast(self, long i)

cdef class ItemType(object):
    cdef readonly long item_length
    cdef readonly long size_tag

    cpdef get_type(self)
    cpdef read_item(self, List lst, long offset)
    cpdef long offset_for_item(self, List lst, long i)
    cpdef bint can_compare(self)
    cpdef write_item(self, SegmentBuilder builder, long post, object item)

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
    cdef readonly type structcls
    cdef readonly long static_data_size
    cdef readonly long static_ptrs_size

cdef class TextItemType(ItemType):
    cdef readonly int additional_size

cdef class ListItemType(ItemType):
    cdef readonly ItemType inner_item_type

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
