import struct
from capnpy.util import mychr

def unpack_uint32(buf, offset):
    if offset < 0 or offset + 4 > len(buf):
        raise IndexError('Offset out of bounds: %d' % offset)
    return struct.unpack_from(b'<I', buf, offset)[0]


class BaseSegment(object):

    def __init__(self, buf):
        assert buf is not None
        self.buf = buf

    def read_primitive(self, offset, ifmt):
        fmt = b'<' + mychr(ifmt)
        if offset < 0 or offset + struct.calcsize(fmt) > len(self.buf):
            raise IndexError('Offset out of bounds: %d' % offset)
        return struct.unpack_from(fmt, self.buf, offset)[0]

    def read_int64(self, offset):
        return self.read_primitive(offset, ord('q'))

    def read_uint64(self, offset):
        return self.read_primitive(offset, ord('Q'))

    def read_uint64_magic(self, offset):
        return self.read_primitive(offset, ord('Q'))

    def read_int32(self, offset):
        return self.read_primitive(offset, ord('i'))

    def read_uint32(self, offset):
        return self.read_primitive(offset, ord('I'))

    def read_int16(self, offset):
        return self.read_primitive(offset, ord('h'))

    def read_uint16(self, offset):
        return self.read_primitive(offset, ord('H'))

    def read_int8(self, offset):
        return self.read_primitive(offset, ord('b'))

    def read_uint8(self, offset):
        return self.read_primitive(offset, ord('B'))

    def read_double(self, offset):
        return self.read_primitive(offset, ord('d'))

    def read_float(self, offset):
        return self.read_primitive(offset, ord('f'))

    def dump_message(self, p, start, end):
        maxlen = len(self.buf)
        if start < 0 or start > end or end > maxlen:
            raise ValueError("start:end values out of bounds: %s:%s" %
                             (start, end))
        segment_count = 1
        length = end-start
        header = struct.pack(b'IIq', (segment_count-1), length//8 + 1, p)
        return header + self.buf[start:end]


BaseSegmentForTests = BaseSegment
