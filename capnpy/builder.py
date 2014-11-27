import struct
from capnpy.blob import Blob

class Builder(object):

    def __init__(self, fmt):
        self._fmt = '<' + fmt # force little endian
        self._size = struct.calcsize(self._fmt)
        self._extra = []
        self._totalsize = self._size # the total size of _extra chunks

    def build(self, *items):
        s = struct.pack(self._fmt, *items)
        return s + ''.join(self._extra)

    def alloc_struct(self, offset, value, expected_type, data_size, ptrs_size):
        if not isinstance(value, expected_type):
            raise TypeError("Expected %s instance, got %s" %
                            (expected_type.__class__.__name__, value))
        # 1) compute the offset of struct relative to the end of the word
        # we are writing to
        ptr_offset = self._totalsize - (offset+8)
        #
        # 2) build the ptrstruct; note that sizes and offsets are expressed in
        # words, not in bytes
        ptr = 0
        ptr |= ptrs_size/8 << 48
        ptr |= data_size/8 << 32
        ptr |= ptr_offset/8 << 2
        ptr |= Blob.PTR_STRUCT
        #
        # 3) append the struct _buf to the end of our stream
        assert len(value._buf) == data_size + ptrs_size
        self._extra.append(value._buf)
        self._totalsize += len(value._buf)
        return ptr
