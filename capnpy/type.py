import struct

class PrimitiveType(object):
    def __init__(self, name, fmt):
        self.name = name
        self.fmt = fmt

    def __repr__(self):
        return '<capnp type %s>' % self.name

    def calcsize(self):
        return struct.calcsize(self.fmt)


class Types(object):

    @classmethod
    def from_which(cls, which):
        # XXX: this is temporary: to bootstrap, we use pycapnp, whose which()
        # returns a string. After bootstrap, which() result will be an Enum.
        return getattr(cls, which)


def make_type(name, fmt):
    t = PrimitiveType(name, fmt)
    setattr(Types, name, t)

make_type('int8',  'b')
make_type('int16', 'h')
make_type('int64', 'q')
make_type('float64', 'd')
