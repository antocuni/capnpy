import struct
from capnpy.pypycompat import setslice8
from capnpy.blob import Blob


class Builder(object):

    def __init__(self, size, maxsize):
        self._array = bytearray(maxsize)
        self._size = size
        self._maxsize = maxsize

    def allocate(self, size):
        newsize = self._size + size
        if newsize > self._maxsize:
            raise ValueError("Cannot allocate %d bytes: maximum size of %d exceeded" %
                             (size, self._maxsize))
        offset = self._size
        self._size = newsize
        return offset

    def build(self):
        return str(self._array[:self._size])

    def _write_primitive(self, fmt, offset, value):
        s = struct.pack(fmt, value)
        setslice8(self._array, offset, s)
        #struct.pack_into(fmt, self._array, offset, value)

    def write_int64(self, offset, value):
        self._write_primitive('<q', offset, value)

    def write_float64(self, offset, value):
        self._write_primitive('<d', offset, value)

    def write_struct(self, offset, value, expected_type, data_size, ptrs_size):
        if not isinstance(value, expected_type):
            raise TypeError("Expected %s instance, got %s" %
                            (expected_type.__class__.__name__, value))
        # 1) compute the offset of struct relative to the end of the word
        # we are writing to
        ptr_offset = (self._size - (offset+8))
        #
        # 2) allocate the space for the struct at the end of the array
        struct_size = data_size + ptrs_size
        struct_offset = self.allocate(struct_size)
        #
        # 3) build the ptrstruct; note that sizes and offsets are expressed in
        # words, not in bytes
        ptr = 0
        ptr |= ptrs_size/8 << 48
        ptr |= data_size/8 << 32
        ptr |= ptr_offset/8 << 2
        ptr |= Blob.PTR_STRUCT
        #
        # 4) write the ptrstruct and the struct
        self.write_int64(offset, ptr)
        self._array[struct_offset:struct_offset+struct_size] = value._buf
