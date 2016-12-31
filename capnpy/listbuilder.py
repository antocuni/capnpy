import struct
from capnpy.blob import Types
from capnpy.builder import AbstractBuilder
from capnpy.printer import BufferPrinter
from capnpy import ptr

class ListBuilder(AbstractBuilder):

    def __init__(self, item_type, item_count):
        self.item_type = item_type
        self.item_length, self.size_tag = item_type.get_item_length()
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
