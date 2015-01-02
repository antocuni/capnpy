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
    pass

def make_type(name, fmt):
    t = PrimitiveType(name, fmt)
    setattr(Types, name, t)

make_type('int8',  'b')
make_type('int16', 'h')
make_type('int64', 'q')
make_type('float64', 'd')
