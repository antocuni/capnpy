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
        # 1) data section
        parts = []
        body_start = item._get_body_start()
        data_size = item_type.__data_size__
        data_buf = item._buf[body_start:body_start+data_size*8]
        parts.append(data_buf)
        #
        # 2) ptrs section
        #    for each ptr:
        #        ptr.offset += new_extra_offset - old_extra_offset
        #
        #    old_extra_offset is the offset of the first extra object in item,
        #    i.e. the ptr.offset of the first ptr
        #
        #    new_extra_offset is the offset of the extra section of the
        #    to-be-written object
        first_ptr = item._read_ptr(item._ptr_offset_by_index(0))
        assert first_ptr.kind != FarPtr.KIND
        old_extra_offset = first_ptr.offset
        item_offset = i * listbuilder.item_length + data_size*8
        new_extra_offset = listbuilder._calc_relative_offset(item_offset)
        additional_offset = new_extra_offset - old_extra_offset
        #
        # iterate over and fix the pointers
        for j in range(item_type.__ptrs_size__):
            # read pointer, update its offset, and pack it
            ptrstart = (data_size+j) * 8
            ptr = item._read_ptr(ptrstart)
            if ptr != 0:
                assert ptr.kind != FarPtr.KIND
                ptr = Ptr.new(ptr.kind, ptr.offset+additional_offset, ptr.extra)
            s = struct.pack('q', ptr)
            parts.append(s)
        #
        extra_start, extra_end = item._get_extra_range()
        extra_buf = item._buf[extra_start:extra_end]
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

