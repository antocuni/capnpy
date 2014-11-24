import struct

class Blob(object):

    PTR_STRUCT = 0
    PTR_LIST = 1

    def __init__(self, buf, offset):
        self._buf = buf
        self._offset = offset

    def _read_int64(self, offset):
        return struct.unpack_from('=q', self._buf, self._offset+offset)[0]

    def _unpack_ptrstruct(self, offset):
        ptr = struct.unpack_from('=q', self._buf, self._offset+offset)[0]
        ptr_kind  = ptr & 0x3
        ptr_offset = ptr>>2 & 0x3fffffff
        data_size = ptr>>32 & 0xffff
        ptrs_size = ptr>>48 & 0xffff
        #
        assert ptr_kind == self.PTR_STRUCT
        return ptr_offset, data_size, ptrs_size
