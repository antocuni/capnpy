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

    def alloc_struct(self, offset, value, expected_type, data_size, ptrs_size):
        if not isinstance(value, expected_type):
            raise TypeError("Expected %s instance, got %s" %
                            (expected_type.__class__.__name__, value))
        #
        ptr_offset = self._calc_relative_offset(offset)
        self._alloc(value._buf, expected_size=data_size+ptrs_size)
        ptr = 0
        ptr |= ptrs_size/8 << 48
        ptr |= data_size/8 << 32
        ptr |= ptr_offset/8 << 2
        ptr |= Blob.PTR_STRUCT
        return ptr

    def alloc_string(self, offset, value):
        value += '\0'
        ptr_offset = self._calc_relative_offset(offset)
        self._alloc(value)
        ptr = 0
        ptr |= len(value) << 35
        ptr |= Blob.LIST_8 << 32
        ptr |= ptr_offset/8 << 2
        ptr |= Blob.PTR_LIST
        return ptr

    def alloc_list(self, offset, listcls, lst):
        ptr_offset = self._calc_relative_offset(offset)
        for item in lst:
            s = struct.pack(listcls.FORMAT, item)
            self._alloc(s)
        ptr = 0
        ptr |= len(lst) << 35
        ptr |= listcls.SIZE_TAG << 32
        ptr |= ptr_offset/8 << 2
        ptr |= Blob.PTR_LIST
        return ptr
        
