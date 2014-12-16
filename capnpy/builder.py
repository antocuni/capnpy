import struct
from capnpy.ptr import StructPtr, ListPtr

class AbstractBuilder(object):

    def __init__(self, length):
        self._length = length
        self._extra = []
        self._total_length = self._length # the total length, including the chunks in _extra

    def _alloc(self, s, aligned=True):
        self._extra.append(s)
        self._total_length += len(s)
        if aligned:
            self._force_alignment()

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
        data_size = struct_type.__data_size__           # in words
        ptrs_size = struct_type.__ptrs_size__           # in words
        ptr_offset = self._calc_relative_offset(offset) # in words
        self._alloc(value._buf)
        ptr = StructPtr.new(ptr_offset, data_size, ptrs_size)
        return ptr

    def alloc_string(self, offset, value):
        if value is None:
            return 0 # NULL
        value += '\0'
        ptr_offset = self._calc_relative_offset(offset)
        ptr = ListPtr.new(ptr_offset, ListPtr.SIZE_8, len(value))
        self._alloc(value)
        return ptr

    def _new_ptrlist(self, size_tag, ptr_offset, item_type, item_count):
        if size_tag != ListPtr.SIZE_COMPOSITE:
            # a plain ptr
            return ListPtr.new(ptr_offset, size_tag, item_count)
        #
        # if size is composite, ptr contains the total size in words, and
        # we also need to emit a "list tag"
        data_size = item_type.__data_size__  # in words
        ptrs_size = item_type.__ptrs_size__  # in words
        total_words = (data_size+ptrs_size) * item_count
        #
        # emit the tag
        tag = StructPtr.new(item_count, data_size, ptrs_size)
        self._alloc(struct.pack('<q', tag))
        return ListPtr.new(ptr_offset/8, ListPtr.SIZE_COMPOSITE, total_words)

    def alloc_list(self, offset, listcls, item_type, lst):
        from capnpy.listbuilder import ListBuilder
        if lst is None:
            return 0 # NULL
        # build the list, using a separate listbuilder
        item_count = len(lst)
        listbuilder = ListBuilder(listcls.ItemBuilder, item_type, item_count)
        for i, item in enumerate(lst):
            s = listcls.ItemBuilder.pack_item(listbuilder, i, item)
            listbuilder.append(s)
        #
        # create the ptrlist, and allocate the list body itself
        ptr_offset = self._calc_relative_offset(offset)
        ptr = self._new_ptrlist(listbuilder.size_tag, ptr_offset, item_type, item_count)
        self._alloc(listbuilder.build())
        return ptr

class StructBuilder(AbstractBuilder):

    def __init__(self, fmt):
        # the size of the main struct
        self._fmt = '<' + fmt # force little endian
        length = struct.calcsize(self._fmt)
        assert length % 8 == 0 # fmt must contains padding bytes, if needed
        AbstractBuilder.__init__(self, length)

    def build(self, *items):
        s = struct.pack(self._fmt, *items)
        return s + ''.join(self._extra)
