import struct
from capnpy.blob import Blob, Types
from capnpy.ptr import Ptr

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
    def get_item_size(cls, item_type):
        size = struct.calcsize(item_type)
        if size == 1:
            return size, Blob.LIST_8
        elif size == 2:
            return size, Blob.LIST_16
        elif size == 4:
            return size, Blob.LIST_32
        elif size == 8:
            return size, Blob.LIST_64
        else:
            raise ValueError('Unsupported size: %d' % size)

    @classmethod
    def pack_item(cls, listbuilder, i, item):
        item_type = listbuilder.item_type
        return struct.pack('<'+item_type, item)

    def _read_list_item(self, offset):
        return self._read_primitive(offset, self._item_type)

class StructList(List):

    @classmethod
    def get_item_size(cls, item_type):
        total_size = item_type.__data_size__ + item_type.__ptrs_size__ # in words
        total_size *= 8 # in bytes
        if total_size > 8:
            return total_size, Blob.LIST_COMPOSITE
        assert False, 'XXX'

    @classmethod
    def pack_item(cls, listbuilder, i, item):
        item_type = listbuilder.item_type
        if not isinstance(item, item_type):
            raise TypeError("Expected an object of type %s, got %s instead" %
                            (item_type.__name__, item.__class__.__name__))
        if item_type.__ptrs_size__ == 0:
            # easy case, just copy the buffer
            return item._buf
        #
        # hard case. The layout of item._buf is like this, where the length of
        # extra might be different for each item
        # +------+------+-------------+
        # | data | ptrs |    extra    |
        # +------+------+-------------+
        #
        # ptrs contains pointers pointing somewhere inside extra. The layout
        # of the list looks like this:
        # +------+------+------+------+....+-------------+----------+....
        # |  D1  |  P1  |  D2  |  P2  |    |    extra1   |  extra2  |
        # +------+------+------+------+....+-------------+----------+....
        #
        # So, to pack an item:
        # 1) the data section is copied verbatim
        # 2) the offset of pointers in ptrs need to be adjusted because extra
        #    will be moved to the end of the list
        # 3) extra must be allocated at the end of the list
        #
        data_size = item_type.__data_size__
        ptrs_size = item_type.__ptrs_size__
        data_buf = item._buf[:data_size*8]

        # XXX: there might be other stuff after extra: we need a way to
        # compute the lenght of extra
        extra_offset = (data_size+ptrs_size)*8
        extra_buf = item._buf[extra_offset:]
        #
        parts = [data_buf]
        offset = i * listbuilder.item_size + data_size*8
        additional_offset = listbuilder._calc_relative_offset(offset)
        #
        # iterate over and fix the pointers
        for j in range(ptrs_size):
            # read pointer, update its offset, and pack it
            ptrstart = (data_size+j) * 8
            ptr = Ptr(item._read_primitive(ptrstart, Types.Int64))
            ptr = Ptr.new(ptr.kind, ptr.offset+additional_offset, ptr.extra)
            s = struct.pack('q', ptr)
            parts.append(s)
        #
        listbuilder._alloc(extra_buf)
        return ''.join(parts)

    def _read_list_item(self, offset):
        return self._item_type.from_buffer(self._buf, self._offset+offset)


class StringList(List):

    @classmethod
    def get_item_size(cls, item_type):
        return 8, Blob.LIST_PTR

    @classmethod
    def pack_item(cls, listbuilder, i, item):
        offset = i * listbuilder.item_size
        ptr = listbuilder.alloc_string(offset, item)
        packed = struct.pack('q', ptr)
        return packed

    def _read_list_item(self, offset):
        return self._read_string(offset)
