import struct
from capnpy.ptr import Ptr, ListPtr, FarPtr
from capnpy.blob import Types
from capnpy.builder import AbstractBuilder
from capnpy.printer import BufferPrinter

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

    def _print_buf(self, **kwds):
        p = BufferPrinter(self.build())
        p.printbuf(**kwds)


class PrimitiveItemBuilder(object):

    @classmethod
    def get_item_length(cls, item_type):
        length = item_type.calcsize()
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
        return struct.pack('<'+item_type.fmt, item)


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
        #
        # In general, the layout of item._buf is like this:
        # +------+------+-------------+
        # | data | ptrs |    extra    |
        # +------+------+-------------+
        #
        # The layout of the list looks like this:
        # +------+------+------+------+....+-------------+----------+....
        # |  D1  |  P1  |  D2  |  P2  |    |    extra1   |  extra2  |
        # +------+------+------+------+....+-------------+----------+....
        #
        # Struct._split takes care to split the body and the extra
        data_size = item_type.__data_size__
        item_offset = i * listbuilder.item_length + data_size*8
        new_extra_offset = listbuilder._calc_relative_offset(item_offset)
        body, extra = item._split(new_extra_offset)
        listbuilder._alloc(extra)
        return body


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

