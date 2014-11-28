import struct
from capnpy.blob import Blob

class Builder(object):

    def __init__(self, fmt):
        self._fmt = '<' + fmt # force little endian
        self._size = struct.calcsize(self._fmt) # the size of the main struct
        self._extra = []
        self._totalsize = self._size # the total size, including the chunks in _extra

    def build(self, *items):
        s = struct.pack(self._fmt, *items)
        return s + ''.join(self._extra)

    def _alloc(self, s, expected_size=None):
        assert expected_size is None or expected_size == len(s)
        self._extra.append(s)
        self._totalsize += len(s)

    def _calc_relative_offset(self, offset):
        return self._totalsize - (offset+8)

    def _new_ptrstruct(self, ptr_offset, data_size, ptrs_size):
        """
        Construct a pointer to struct; data_size and ptrs_size are expressed in
        BYTES (not in words)
        """
        ptr = 0
        ptr |= ptrs_size/8 << 48
        ptr |= data_size/8 << 32
        ptr |= ptr_offset/8 << 2
        ptr |= Blob.PTR_STRUCT
        return ptr

    def _new_ptrlist(self, ptr_offset, size_tag, item_count):
        """
        Construct a pointer to list
        """
        ptr = 0
        ptr |= item_count << 35
        ptr |= size_tag << 32
        ptr |= ptr_offset/8 << 2
        ptr |= Blob.PTR_LIST
        return ptr

    def _new_ptrlist_composite(self, ptr_offset, item_type, item_count):
        # if size is composite, ptr contains the total size in words, and
        # we also need to emit a "list tag"
        data_size = item_type.__data_size__  # in bytes
        ptrs_size = item_type.__ptrs_size__  # in bytes
        total_words = (data_size+ptrs_size)/8 * item_count
        #
        # emit the tag
        # we need to pass item_count*8, because _new_ptrstruct divides by 8 internally
        tag = self._new_ptrstruct(item_count*8, data_size, ptrs_size)
        self._alloc(struct.pack('<q', tag))
        #
        return self._new_ptrlist(ptr_offset, Blob.LIST_COMPOSITE, total_words)

    def alloc_struct(self, offset, struct_type, value):
        if value is None:
            return 0 # NULL
        if not isinstance(value, struct_type):
            raise TypeError("Expected %s instance, got %s" %
                            (struct_type.__class__.__name__, value))
        #
        data_size = struct_type.__data_size__
        ptrs_size = struct_type.__ptrs_size__
        ptr_offset = self._calc_relative_offset(offset)
        self._alloc(value._buf, expected_size=data_size+ptrs_size)
        ptr = self._new_ptrstruct(ptr_offset, data_size, ptrs_size)
        return ptr

    def alloc_string(self, offset, value):
        if value is None:
            return 0 # NULL
        value += '\0'
        ptr_offset = self._calc_relative_offset(offset)
        self._alloc(value)
        ptr = self._new_ptrlist(ptr_offset, Blob.LIST_8, len(value))
        return ptr

    def alloc_list(self, offset, listcls, item_type, lst):
        if lst is None:
            return 0 # NULL
        ptr_offset = self._calc_relative_offset(offset)
        size_tag = listcls.get_size_tag(item_type)
        item_count = len(lst)
        if size_tag == Blob.LIST_COMPOSITE:
            ptr = self._new_ptrlist_composite(ptr_offset, item_type, item_count)
        else:
            ptr = self._new_ptrlist(ptr_offset, size_tag, item_count)
        #
        for item in lst:
            s = listcls.pack_item(item_type, item)
            self._alloc(s)
        #
        return ptr
