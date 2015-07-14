import struct
def unpack_primitive(fmt, buf, offset):
    return struct.unpack_from('<' + fmt, buf, offset)[0]
