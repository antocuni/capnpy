import struct
def unpack_primitive(ifmt, buf, offset):
    fmt = '<' + chr(ifmt)
    if offset < 0 or offset + struct.calcsize(fmt) > len(buf):
        raise IndexError('Offset out of bounds: %d' % offset)
    return struct.unpack_from(fmt, buf, offset)[0]
