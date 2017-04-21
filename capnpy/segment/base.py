import struct
from pypytools import IS_PYPY

if IS_PYPY:
    # workaround for a limitation of the PyPy JIT: struct.unpack is optimized
    # only if the format string is a tracing-time constant; this is because of
    # this line in rlib/rstruct/formatiterator.py:
    #    @jit.look_inside_iff(lambda self, fmt: jit.isconstant(fmt))
    #    def interpret(self, fmt):
    #        ...
    #
    # The problem is that if you use struct.unpack(chr(113), '...'), chr(113)
    # is not a tracing-time constant (it becomes constant later, during
    # optimizeopt). The work around is to use mychr, which pyjitpl.py is smart
    # enough to detect as a tracing-time constant.
    _CHR = tuple(map(chr, range(256)))
    def mychr(i):
        return _CHR[i]

else:
    mychr = chr


def unpack_uint32(buf, offset):
    if offset < 0 or offset + 4 > len(buf):
        raise IndexError('Offset out of bounds: %d' % offset)
    return struct.unpack_from('<I', buf, offset)[0]


class BaseSegment(object):

    def __init__(self, buf):
        assert buf is not None
        self.buf = buf

    def read_primitive(self, offset, ifmt):
        fmt = '<' + mychr(ifmt)
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
        header = struct.pack('IIq', (segment_count-1), length/8 + 1, p)
        return header + self.buf[start:end]

BaseSegmentForTests = BaseSegment
