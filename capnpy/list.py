import struct
import capnpy
from capnpy.blob import Blob, Types
from capnpy.ptr import Ptr, StructPtr, ListPtr
from capnpy import listbuilder

class List(Blob):

    @classmethod
    def from_buffer(cls, buf, offset, size_tag, item_count, item_type):
        """
        buf, offset: the underlying buffer and the offset where the list starts

        item_length: the length of each list item, in BYTES. Note: this is NOT the
        value of the ListPtr.SIZE_* tag, although it's obviously based on it

        item_type: the type of each list item. Either a Blob/Struct subclass,
        or a Types.*
        """
        self = super(List, cls).from_buffer(buf, offset)
        self._item_type = item_type
        self._set_list_tag(size_tag, item_count)
        return self

    def _set_list_tag(self, size_tag, item_count):
        self._size_tag = size_tag
        if size_tag == ListPtr.SIZE_COMPOSITE:
            tag = self._read_primitive(0, Types.Int64)
            tag = StructPtr(tag)
            self._tag = tag
            self._item_count = tag.offset
            self._item_length = (tag.data_size+tag.ptrs_size)*8
            self._item_offset = 8
        elif size_tag == ListPtr.SIZE_BIT:
            raise ValueError('Lists of bits are not supported')
        else:
            self._tag = None
            self._item_count = item_count
            self._item_length = ListPtr.SIZE_LENGTH[size_tag]
            self._item_offset = 0


    def _read_list_item(self, offset):
        raise NotImplementedError

    def _get_offset_for_item(self, i):
        return self._item_offset + (i*self._item_length)
            
    def __len__(self):
        return self._item_count

    def __getitem__(self, i):
        if i < 0:
            i += self._item_count
        if 0 <= i < self._item_count:
            offset = self._get_offset_for_item(i)
            return self._read_list_item(offset)
        raise IndexError

    def _get_body_range(self):
        return self._get_body_start(), self._get_body_end()

    def _get_body_start(self):
        return self._offset

    def _get_body_end(self):
        if self._size_tag == ListPtr.SIZE_COMPOSITE:
            # lazy access to GenericStruct to avoid circular imports
            GenericStruct = capnpy.struct_.GenericStruct
            struct_offset = self._get_offset_for_item(self._item_count-1)
            struct_offset += self._offset
            mystruct = GenericStruct.from_buffer_and_size(self._buf,
                                                          struct_offset,
                                                          self._tag.data_size,
                                                          self._tag.ptrs_size)
            return mystruct._get_extra_end()
        elif self._size_tag == ListPtr.SIZE_PTR:
            ptr_offset = self._get_offset_for_item(self._item_count-1)
            blob = self._follow_generic_pointer(ptr_offset)
            return blob._get_end()
        else:
            return self._offset + self._item_length*self._item_count

    def _get_end(self):
        return self._get_body_end()


class PrimitiveList(List):
    ItemBuilder = listbuilder.PrimitiveItemBuilder
    
    def _read_list_item(self, offset):
        return self._read_primitive(offset, self._item_type)

class StructList(List):
    ItemBuilder = listbuilder.StructItemBuilder

    def _read_list_item(self, offset):
        return self._item_type.from_buffer(self._buf, self._offset+offset)


class StringList(List):
    ItemBuilder = listbuilder.StringItemBuilder

    def _read_list_item(self, offset):
        return self._read_string(offset)

