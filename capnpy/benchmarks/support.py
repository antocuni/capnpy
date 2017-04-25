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
                     intlist, color):
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
            self.color = color

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

    class Rectangle(object):
        def __init__(self, a, b):
            self.a = a
            self.b = b

    class MyStructContainer(object):
        def __init__(self, items):
            self.items = items

    MyInt64List = MyStructContainer


# ============================================================
# Namedtuple storage
# ============================================================

class NamedTuple(object):

    _Base = namedtuple('_Base', ['padding', 'bool', 'int8', 'int16',
                                 'int32', 'int64', 'uint8', 'uint16',
                                 'uint32', 'uint64', 'float32',
                                 'float64', 'text', 'group', 'inner', 'intlist',
                                 'color'])

    MyGroup = namedtuple('MyGroup', ['field'])
    MyInner = namedtuple('MyInner', ['field'])

    class MyStruct(_Base):

        def __new__(cls, padding, bool, int8, int16, int32, int64, uint8,
                    uint16, uint32, uint64, float32, float64, text, group, inner,
                    intlist, color):
            group = NamedTuple.MyGroup(*group)
            return NamedTuple._Base.__new__(
                cls, padding, bool, int8, int16, int32, int64,
                uint8, uint16, uint32, uint64, float32, float64,
                text, group, inner, intlist, color)

    Point = namedtuple('Point', ['x', 'y', 'z'])
    StrPoint = namedtuple('StrPoint', ['x', 'y', 'z'])
    Rectangle = namedtuple('Rectangle', ['a', 'b'])
    MyStructContainer = namedtuple('MyStructContainer', ['items'])
    MyInt64List = namedtuple('MyInt64List', ['items'])

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
                    uint64, float32, float64, text, group, inner, intlist,
                    color):
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
            s.color = color
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

    @staticmethod
    def StrPoint(x, y, z):
        if pycapnp is None:
            py.test.skip('cannot import pycapnp')
        s = pycapnp_schema.StrPoint.new_message()
        s.x = x
        s.y = y
        s.z = z
        return pycapnp_schema.StrPoint.from_bytes(s.to_bytes())

    @staticmethod
    def Rectangle(a, b):
        if pycapnp is None:
            py.test.skip('cannot import pycapnp')
        s = pycapnp_schema.Rectangle.new_message()
        s.a = a
        s.b = b
        return pycapnp_schema.Rectangle.from_bytes(s.to_bytes())

    @staticmethod
    def MyStructContainer(items):
        if pycapnp is None:
            py.test.skip('cannot import pycapnp')
        s = pycapnp_schema.MyStructContainer.new_message()
        s.items = items
        return pycapnp_schema.MyStructContainer.from_bytes(s.to_bytes())

    @staticmethod
    def MyInt64List(items):
        if pycapnp is None:
            py.test.skip('cannot import pycapnp')
        s = pycapnp_schema.MyInt64List.new_message()
        s.items = items
        return pycapnp_schema.MyInt64List.from_bytes(s.to_bytes())

    class Tree(object):
        @staticmethod
        def loads(s):
            if pycapnp is None:
                py.test.skip('cannot import pycapnp')
            # this tree/newtree dance it's needed because 'tree' has a message
            # traversal limit: since we read the same message again and again
            # in the benchmark, we construct a newtree, whose traversal limit
            # is not set
            tree = pycapnp_schema.Tree.from_bytes(s)
            newtree = pycapnp_schema.Tree.new_message()
            newtree.root = tree.root
            return newtree

        def __new__(cls, root):
            msg = pycapnp_schema.Tree.new_message()
            msg.root = root
            return msg
