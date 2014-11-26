import struct

class Builder(object):

    def __init__(self, maxsize):
        self._array = bytearray(maxsize)
        self._maxsize = maxsize
        self._size = 0

    def allocate(self, size):
        newsize = self._size + size
        if newsize > self._maxsize:
            raise ValueError("Cannot allocate %d bytes: maximum size of %d exceeded" %
                             (size, self._maxsize))
        self._size = newsize

    def _write_primitive(self, fmt, offset, value):
        struct.pack_into(fmt, self._array, offset, value)

    def write_int64(self, offset, value):
        self._write_primitive('<q', offset, value)

    def write_float64(self, offset, value):
        self._write_primitive('<d', offset, value)

    def build(self):
        return str(self._array[:self._size])
