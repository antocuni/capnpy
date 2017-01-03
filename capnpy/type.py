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
Types._make('int8',    'b')
Types._make('uint8',   'B')
Types._make('int16',   'h')
Types._make('uint16',  'H')
Types._make('int32',   'i')
Types._make('uint32',  'I')
Types._make('int64',   'q')
Types._make('uint64',  'Q')
Types._make('float32', 'f')
Types._make('float64', 'd')
Types._make('text')
Types._make('data')

