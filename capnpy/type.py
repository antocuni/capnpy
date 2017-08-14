import struct

class BuiltinType(object):
    def __init__(self, name, fmt=None):
        self.name = name
        self.fmt = fmt
        if fmt is not None:
            self.ifmt = ord(fmt)
        else:
            self.ifmt = -1

    def __repr__(self):
        return '<capnp type %s>' % self.name

    def is_primitive(self):
        return self.fmt is not None

    def calcsize(self):
        return struct.calcsize(self.fmt)


class Types(object):

    __all__ = []

    @classmethod
    def _make(cls, name, fmt=None):
        t = BuiltinType(name, fmt)
        setattr(cls, name, t)
        cls.__all__.append(t)


Types._make('void')
Types._make('bool')
Types._make('int8',    b'b')
Types._make('uint8',   b'B')
Types._make('int16',   b'h')
Types._make('uint16',  b'H')
Types._make('int32',   b'i')
Types._make('uint32',  b'I')
Types._make('int64',   b'q')
Types._make('uint64',  b'Q')
Types._make('float32', b'f')
Types._make('float64', b'd')
Types._make('text')
Types._make('data')

