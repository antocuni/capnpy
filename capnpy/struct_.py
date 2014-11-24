import struct

class Struct(object):

    def __init__(self, buf, offset):
        self._buf = buf
        self._offset = offset

    @classmethod
    def from_buffer(cls, buf, offset):
        return cls(buf, offset)

    def _read_int64(self, offset):
        return struct.unpack_from('=q', self._buf, offset+self._offset)[0]
