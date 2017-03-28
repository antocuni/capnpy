import struct

class Segment(object):

    def __init__(self, buf):
        self.buf = buf

    def read_primitive(self, fmt, offset):
        fmt = '<' + fmt
        if offset < 0 or offset + struct.calcsize(fmt) > len(self.buf):
            raise IndexError('Offset out of bounds: %d' % offset)
        return struct.unpack_from(fmt, self.buf, offset)[0]

    def read_int64(self, offset):
        return self.read_primitive('q', offset)

    def read_uint64(self, offset):
        return self.read_primitive('Q', offset)

    def read_uint64_magic(self, offset):
        return self.read_primitive('Q', offset)

    def read_int32(self, offset):
        return self.read_primitive('i', offset)

    def read_uint32(self, offset):
        return self.read_primitive('I', offset)

    def read_int16(self, offset):
        return self.read_primitive('h', offset)

    def read_uint16(self, offset):
        return self.read_primitive('H', offset)

    def read_int8(self, offset):
        return self.read_primitive('b', offset)

    def read_uint8(self, offset):
        return self.read_primitive('B', offset)

    def read_double(self, offset):
        return self.read_primitive('d', offset)

    def read_float(self, offset):
        return self.read_primitive('f', offset)


class SegmentBuilder(object):
    pass
