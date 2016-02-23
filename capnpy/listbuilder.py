import struct
from capnpy.blob import Types
from capnpy.builder import AbstractBuilder
from capnpy.printer import BufferPrinter
from capnpy import ptr

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
            return length, ptr.LIST_SIZE_8
        elif length == 2:
            return length, ptr.LIST_SIZE_16
        elif length == 4:
            return length, ptr.LIST_SIZE_32
        elif length == 8:
            return length, ptr.LIST_SIZE_64
        else:
            raise ValueError('Unsupported size: %d' % length)

    @classmethod
    def pack_item(cls, listbuilder, i, item):
        item_type = listbuilder.item_type
        return struct.pack('<'+item_type.fmt, item)


class StructItemBuilder(object):

    @classmethod
    def get_item_length(cls, item_type):
        total_size = (item_type.__static_data_size__ +
                      item_type.__static_ptrs_size__)   # in words
        total_length = total_size*8                     # in bytes
        if total_length > 8:
            return total_length, ptr.LIST_SIZE_COMPOSITE
        assert False, 'XXX'

    @classmethod
    def pack_item(cls, listbuilder, i, item):
        item_type = listbuilder.item_type
        if not isinstance(item, item_type):
            raise TypeError("Expected an object of type %s, got %s instead" %
                            (item_type.__name__, item.__class__.__name__))
        #
        # This is the layout of the list:
        #
        # +-------+-------+...+-------+--------+--------+...+--------+
        # | body0 | body1 |   | bodyN | extra0 | extra1 |   | extraN |
        # +-------+-------+...+-------+--------+--------+...+--------+
        # |               |                    |
        # |- body_offset -|                    |
        # |               |--- extra_offset ---|
        # |                                    |
        # +------- _total_length --------------+
        #
        # When i==1, self._total_length will contain the offset up to the end
        # of extra0; extra1...extraN are not yet considered.
        #
        # The item body and extra are split by Struct._split, passing the
        # correct extra_offset.
        #
        # Note that extra_offset is expressed in WORDS, while _total_length in
        # BYTES
        body_size = item_type.__static_data_size__ + item_type.__static_ptrs_size__
        body_offset = body_size * (i+1)
        extra_offset = listbuilder._total_length/8 - body_offset
        body, extra = item._split(extra_offset)
        listbuilder._alloc(extra)
        return body


class StringItemBuilder(object):

    @classmethod
    def get_item_length(cls, item_type):
        return 8, ptr.LIST_SIZE_PTR

    @classmethod
    def pack_item(cls, listbuilder, i, item):
        offset = i * listbuilder.item_length
        ptr = listbuilder.alloc_text(offset, item)
        packed = struct.pack('q', ptr)
        return packed

