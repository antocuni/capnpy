import struct
from capnpy.ptr import Ptr, ListPtr
from capnpy.blob import Types
from capnpy.builder import AbstractBuilder

class ListBuilder(AbstractBuilder):

    def __init__(self, item_builder, item_type, item_count):
        self.item_builder = item_builder
        self.item_type = item_type
        self.item_length, self.size_tag = item_builder.get_item_length(item_type)
        self.item_count = item_count
        self._items = []
        length = self.item_length * self.item_count
        AbstractBuilder.__init__(self, length)
        self._force_alignment()

    def append(self, item):
        self._items.append(item)

    def build(self):
        assert len(self._items) == self.item_count
        listbody = ''.join(self._items)
        assert len(listbody) == self._length
        return listbody + ''.join(self._extra)


class PrimitiveItemBuilder(object):

    @classmethod
    def get_item_length(cls, item_type):
        length = struct.calcsize(item_type)
        if length == 1:
            return length, ListPtr.SIZE_8
        elif length == 2:
            return length, ListPtr.SIZE_16
        elif length == 4:
            return length, ListPtr.SIZE_32
        elif length == 8:
            return length, ListPtr.SIZE_64
        else:
            raise ValueError('Unsupported size: %d' % length)

    @classmethod
    def pack_item(cls, listbuilder, i, item):
        item_type = listbuilder.item_type
        return struct.pack('<'+item_type, item)


class StructItemBuilder(object):

    @classmethod
    def get_item_length(cls, item_type):
        total_size = item_type.__data_size__ + item_type.__ptrs_size__ # in words
        total_length = total_size*8 # in bytes
        if total_length > 8:
            return total_length, ListPtr.SIZE_COMPOSITE
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
        offset = i * listbuilder.item_length + data_size*8
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


class StringItemBuilder(object):

    @classmethod
    def get_item_length(cls, item_type):
        return 8, ListPtr.SIZE_PTR

    @classmethod
    def pack_item(cls, listbuilder, i, item):
        offset = i * listbuilder.item_length
        ptr = listbuilder.alloc_string(offset, item)
        packed = struct.pack('q', ptr)
        return packed

