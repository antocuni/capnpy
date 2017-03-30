import struct

class SegmentBuilder(object):

    WIP = True

    def __init__(self, length=None):
        self.buf = bytearray()

    def allocate(self, length):
        # XXX: check whether there is a better method to zero-extend the array in PyPy
        result = len(self.buf)
        self.buf += '\x00'*length
        return result

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

