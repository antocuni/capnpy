import struct
from capnpy.blob import Blob

class List(Blob):

    @classmethod
    def from_buffer(cls, buf, offset, item_size, item_count, item_type):
        """
        buf, offset: the underlying buffer and the offset where the list starts

        item_size: the size of each list item, in BYTES. Note: this is NOT the
        value of the LIST_* tag, although it's obviously based on it

        item_type: the type of each list item. Either a Blob/Struct subclass,
        or a Types.*
        """
        self = super(List, cls).from_buffer(buf, offset)
        self._item_size = item_size
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
            offset = (i*self._item_size)
            return self._read_list_item(offset)
        raise IndexError


class PrimitiveList(List):

    @classmethod
    def pack_item(cls, item_type, item):
        return struct.pack('<'+item_type, item)

    @classmethod
    def get_size_tag(cls, item_type):
        size = struct.calcsize(item_type)
        if size == 1:
            return Blob.LIST_8
        elif size == 2:
            return Blob.LIST_16
        elif size == 4:
            return Blob.LIST_32
        elif size == 8:
            return Blob.LIST_64
        else:
            raise ValueError('Unsupported size: %d' % size)

    def _read_list_item(self, offset):
        return self._read_primitive(offset, self._item_type)

class StructList(List):

    @classmethod
    def pack_item(cls, item_type, item):
        raise NotImplementedError

    @classmethod
    def get_size_tag(cls, item_type):
        raise NotImplementedError

    def _read_list_item(self, offset):
        return self._item_type.from_buffer(self._buf, self._offset+offset)
