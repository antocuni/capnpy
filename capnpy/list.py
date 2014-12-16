import struct
from capnpy.blob import Blob, Types
from capnpy.ptr import Ptr, ListPtr
from capnpy import listbuilder

class List(Blob):

    @classmethod
    def from_buffer(cls, buf, offset, item_length, item_count, item_type):
        """
        buf, offset: the underlying buffer and the offset where the list starts

        item_length: the length of each list item, in BYTES. Note: this is NOT the
        value of the ListPtr.SIZE_* tag, although it's obviously based on it

        item_type: the type of each list item. Either a Blob/Struct subclass,
        or a Types.*
        """
        self = super(List, cls).from_buffer(buf, offset)
        self._item_length = item_length
        self._item_count = item_count
        self._item_type = item_type
        return self

    def _read_list_item(self, offset):
        raise NotImplementedError

    def __len__(self):
        return self._item_count

    def __getitem__(self, i):
        if i < 0:
            i += self._item_count
        if 0 <= i < self._item_count:
            offset = (i*self._item_length)
            return self._read_list_item(offset)
        raise IndexError

    def _get_body_range(self):
        start = self._offset
        end = self._offset + self._item_length*self._item_count
        # XXX: handle SIZE_COMPOSITE case
        return start, end


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
