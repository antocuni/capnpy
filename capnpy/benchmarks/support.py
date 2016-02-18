import py
from collections import namedtuple

# ============================================================
# Instance storage
# ============================================================

class Instance(object):
    def __init__(self, padding, bool, int8, int16, int32, int64, uint8,
                 uint16, uint32, uint64, float32, float64, text, group):
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
        self.group = Instance_Group(*group)

class Instance_Group(object):
    def __init__(self, field):
        self.field = field




# ============================================================
# Namedtuple storage
# ============================================================

BaseNamedTuple = namedtuple('BaseNamedTuple', ['padding', 'bool', 'int8', 'int16',
                                               'int32', 'int64', 'uint8', 'uint16',
                                               'uint32', 'uint64', 'float32',
                                               'float64', 'text', 'group'])
NamedTuple_Group = namedtuple('NamedTuple_Group', ['field'])

class NamedTuple(BaseNamedTuple):

    def __new__(cls, padding, bool, int8, int16, int32, int64, uint8,
                uint16, uint32, uint64, float32, float64, text, group):
        group = NamedTuple_Group(group)
        return BaseNamedTuple.__new__(cls, padding, bool, int8, int16, int32, int64,
                                      uint8, uint16, uint32, uint64, float32, float64,
                                      text, group)



# ============================================================
# pycapnp storage
# ============================================================

try:
    import capnp as pycapnp
except ImportError:
    pycapnp = None
else:
    thisdir = py.path.local(__file__).dirpath()
    pycapnp_schema = pycapnp.load(str(thisdir.join('benchmarks.capnp')))

def pycapnp_struct(padding, bool, int8, int16, int32, int64, uint8, uint16, uint32,
                   uint64, float32, float64, text, group):
    if pycapnp is None:
        py.test.skip('cannot import pycapnp')
    s = pycapnp_schema.CapnpStruct.new_message()
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
    return pycapnp_schema.CapnpStruct.from_bytes(s.to_bytes())
