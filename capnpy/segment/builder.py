import struct
from capnpy import ptr

def round_to_word(pos):
    return (pos + (8 - 1)) & -8  # Round up to 8-byte boundary

class SegmentBuilder(object):

    WIP = True

    def __init__(self, length=None):
        self.buf = bytearray()

    def as_string(self):
        return str(self.buf)

    def write_int8(self, i, value):
        struct.pack_into('b', self.buf, i, value)

    def write_uint8(self, i, value):
        struct.pack_into('B', self.buf, i, value)

    def write_int16(self, i, value):
        struct.pack_into('h', self.buf, i, value)

    def write_uint16(self, i, value):
        struct.pack_into('H', self.buf, i, value)

    def write_int32(self, i, value):
        struct.pack_into('i', self.buf, i, value)

    def write_uint32(self, i, value):
        struct.pack_into('I', self.buf, i, value)

    def write_int64(self, i, value):
        struct.pack_into('q', self.buf, i, value)

    def write_uint64(self, i, value):
        struct.pack_into('Q', self.buf, i, value)

    def write_float(self, i, value):
        struct.pack_into('f', self.buf, i, value)

    def write_double(self, i, value):
        struct.pack_into('d', self.buf, i, value)

    def allocate(self, length):
        # XXX: check whether there is a better method to zero-extend the array in PyPy
        result = len(self.buf)
        self.buf += '\x00'*length
        return result

    def alloc_struct(self, pos, data_size, ptrs_size):
        """
        Allocate a new struct of the given size, and write the resulting pointer
        at position i. Return the newly allocated position.
        """
        length = (data_size+ptrs_size) * 8
        result = self.allocate(length)
        offet = result - (pos+8)
        p = ptr.new_struct(offet/8, data_size, ptrs_size)
        self.write_int64(pos, p)
        return result

    def alloc_list(self, pos, size_tag, item_count, body_length):
        """
        Allocate a new list of the given size, and write the resulting pointer
        at position i. Return the newly allocated position.
        """
        body_length = round_to_word(body_length)
        result = self.allocate(body_length)
        offet = result - (pos+8)
        p = ptr.new_list(offet/8, size_tag, item_count)
        self.write_int64(pos, p)
        return result


