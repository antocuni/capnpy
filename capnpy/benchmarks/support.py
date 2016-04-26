import py
from collections import namedtuple
import capnpy

# ============================================================
# Instance storage
# ============================================================

class Instance(object):

    class MyStruct(object):
        def __init__(self, padding, bool, int8, int16, int32, int64, uint8,
                     uint16, uint32, uint64, float32, float64, text, group, inner,
                     intlist):
            self.padding = padding
            self.bool = bool
            self.int8 = int8
            self.int16 = int16
            self.int32 = int32
            self.int64 = int64
            self.uint8 = uint8
            self.uint16 = uint16
            self.uint32 = uint32
            self.uint64 = uint64
            self.float32 = float32
            self.float64 = float64
            self.text = text
            self.group = Instance.MyGroup(*group)
            self.inner = inner
            self.intlist = intlist

    class MyGroup(object):
        def __init__(self, field):
            self.field = field

    class MyInner(object):
        def __init__(self, field):
            self.field = field

    class Point(object):
        def __init__(self, x, y, z):
            self.x = x
            self.y = y
            self.z = z

        def __hash__(self):
            return hash((self.x, self.y, self.z))

    class StrPoint(object):
        def __init__(self, x, y, z):
            self.x = x
            self.y = y
            self.z = z

        def __hash__(self):
            return hash((self.x, self.y, self.z))

# ============================================================
# Namedtuple storage
# ============================================================

class NamedTuple(object):

    _Base = namedtuple('_Base', ['padding', 'bool', 'int8', 'int16',
                                 'int32', 'int64', 'uint8', 'uint16',
                                 'uint32', 'uint64', 'float32',
                                 'float64', 'text', 'group', 'inner', 'intlist'])

    MyGroup = namedtuple('MyGroup', ['field'])
    MyInner = namedtuple('MyInner', ['field'])

    class MyStruct(_Base):

        def __new__(cls, padding, bool, int8, int16, int32, int64, uint8,
                    uint16, uint32, uint64, float32, float64, text, group, inner,
                    intlist):
            group = NamedTuple.MyGroup(*group)
            return NamedTuple._Base.__new__(
                cls, padding, bool, int8, int16, int32, int64,
                uint8, uint16, uint32, uint64, float32, float64,
                text, group, inner, intlist)

    Point = namedtuple('Point', ['x', 'y', 'z'])
    StrPoint = namedtuple('StrPoint', ['x', 'y', 'z'])

# ============================================================
# capnpy storage
# ============================================================

Capnpy = capnpy.load_schema('capnpy.benchmarks.benchmarks')


# ============================================================
# pycapnp storage
# ============================================================

try:
    import capnp as pycapnp
except ImportError:
    pycapnp = None
else:
    thisdir = py.path.local(__file__).dirpath()
    rootdir = thisdir.dirpath('..')
    pycapnp_schema = pycapnp.load(str(thisdir.join('benchmarks.capnp')),
                                  imports=[str(rootdir)])

class PyCapnp(object):

    # this is a fake class, as __new__ returns objects of a different
    # class. We simply use it as a namespace
    class MyStruct(object):

        def __new__(cls, padding, bool, int8, int16, int32, int64, uint8, uint16, uint32,
                    uint64, float32, float64, text, group, inner, intlist):
            if pycapnp is None:
                py.test.skip('cannot import pycapnp')
            s = pycapnp_schema.MyStruct.new_message()
            s.padding = padding
            s.bool = bool
            s.int8 = int8
            s.int16 = int16
            s.int32 = int32
            s.int64 = int64
            s.uint8 = uint8
            s.uint16 = uint16
            s.uint32 = uint32
            s.uint64 = uint64
            s.float32 = float32
            s.float64 = float64
            s.text = text
            s.group.field = group[0]
            s.inner = inner
            s.intlist = intlist
            return pycapnp_schema.MyStruct.from_bytes(s.to_bytes())

        @classmethod
        def load(cls, f):
            if pycapnp is None:
                py.test.skip('cannot import pycapnp')
            return pycapnp_schema.MyStruct.read(f)


    @staticmethod
    def MyInner(field):
        if pycapnp is None:
            py.test.skip('cannot import pycapnp')
        s = pycapnp_schema.MyInner.new_message()
        s.field = field
        return pycapnp_schema.MyInner.from_bytes(s.to_bytes())

    @staticmethod
    def Point(x, y, z):
        if pycapnp is None:
            py.test.skip('cannot import pycapnp')
        s = pycapnp_schema.Point.new_message()
        s.x = x
        s.y = y
        s.z = z
        return pycapnp_schema.Point.from_bytes(s.to_bytes())

