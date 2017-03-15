import struct
from capnpy import ptr
from capnpy.type import Types
from capnpy.packing import unpack_primitive, mychr, pack_into, pack_int64_into
from capnpy.printer import BufferPrinter

class AbstractBuilder(object):

    def __init__(self, length):
        self._length = length
        self._extra = []
        self._total_length = self._length # the total length, including the chunks in _extra

    def _alloc(self, s):
        self._extra.append(s)
        self._total_length += len(s)
        self._force_alignment()

    def _record_allocation(self, offset, p):
        pass

    def _force_alignment(self):
        padding = 8 - (self._total_length % 8)
        if padding != 8:
            self._extra.append('\x00'*padding)
            self._total_length += padding

    def _calc_relative_offset(self, offset):
        return (self._total_length - (offset+8)) / 8

    def alloc_struct(self, offset, struct_type, value):
        if value is None:
            return 0 # NULL
        if not isinstance(value, struct_type):
            raise TypeError("Expected %s instance, got %s" %
                            (struct_type.__class__.__name__, value))
        #
        data_size = value._data_size                    # in words
        ptrs_size = value._ptrs_size                    # in words
        ptr_offset = self._calc_relative_offset(offset) # in words
        #
        # we need to take the compact repr of the struct, else we might get
        # garbage and wrong offsets. See
        # test_alloc_list_of_structs_with_pointers
        p = ptr.new_struct(ptr_offset, data_size, ptrs_size)
        self._alloc(value.compact()._buf.s)
        self._record_allocation(offset, p)
        return p

    def alloc_data(self, offset, value, suffix=None):
        if value is None:
            return 0 # NULL
        if suffix:
            value += suffix
        ptr_offset = self._calc_relative_offset(offset)
        p = ptr.new_list(ptr_offset, ptr.LIST_SIZE_8, len(value))
        self._alloc(value)
        self._record_allocation(offset, p)
        return p

    def alloc_text(self, offset, value):
        return self.alloc_data(offset, value, suffix=b'\0')

    def _new_ptrlist(self, size_tag, ptr_offset, item_type, item_count):
        if size_tag != ptr.LIST_SIZE_COMPOSITE:
            # a plain ptr
            return ptr.new_list(ptr_offset, size_tag, item_count)
        #
        # if size is composite, ptr contains the total size in words, and
        # we also need to emit a "list tag"
        data_size = item_type.structcls.__static_data_size__  # in words
        ptrs_size = item_type.structcls.__static_ptrs_size__  # in words
        total_words = (data_size+ptrs_size) * item_count
        #
        # emit the tag
        tag = ptr.new_struct(item_count, data_size, ptrs_size)
        self._alloc(struct.pack('<q', tag))
        return ptr.new_list(ptr_offset, ptr.LIST_SIZE_COMPOSITE, total_words)

    def alloc_list(self, offset, item_type, lst):
        if lst is None:
            return 0 # NULL
        # build the list, using a separate listbuilder
        item_count = len(lst)
        listbuilder = ListBuilder(item_type, item_count)
        for i, item in enumerate(lst):
            s = item_type.pack_item(listbuilder, i, item)
            listbuilder.append(s)
        #
        # create the ptrlist, and allocate the list body itself
        ptr_offset = self._calc_relative_offset(offset)
        ptr = self._new_ptrlist(listbuilder.size_tag, ptr_offset, item_type, item_count)
        self._alloc(listbuilder.build())
        self._record_allocation(offset, ptr)
        return ptr


class Builder(AbstractBuilder):

    def __init__(self, data_size, ptrs_size):
        length = (data_size + ptrs_size) * 8
        AbstractBuilder.__init__(self, length)
        self._buf = bytearray(length)

    def _record_allocation(self, offset, p):
        # write the pointer on the wire
        pack_int64_into(self._buf, offset, p)

    def set(self, ifmt, offset, value):
        pack_into(ifmt, self._buf, offset, value)

    def setbool(self, byteoffset, bitoffset, value):
        ifmt = Types.uint8.ifmt
        current = unpack_primitive(ifmt, self._buf, byteoffset)
        current |= (value << bitoffset)
        self.set(ifmt, byteoffset, current)

    def build(self):
        return str(self._buf) + ''.join(self._extra)


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
