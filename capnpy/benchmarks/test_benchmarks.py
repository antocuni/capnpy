import py
import pytest
import pypytools
from pypytools.codegen import Code
from collections import namedtuple
import capnpy

try:
    import capnp as pycapnp
except ImportError:
    pycapnp = None
else:
    thisdir = py.path.local(__file__).dirpath()
    pycapnp_schema = pycapnp.load(str(thisdir.join('benchmarks.capnp')))


schema = capnpy.load_schema('capnpy.benchmarks.benchmarks')

NamedTuple = namedtuple('NamedTuple', ['padding', 'bool', 'int8', 'int16', 'int32', 'int64',
                                       'uint8', 'uint16', 'uint32', 'uint64', 'float32',
                                       'float64', 'text'])

class Instance(object):
    def __init__(self, padding, bool, int8, int16, int32, int64, uint8,
                 uint16, uint32, uint64, float32, float64, text):
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


def pycapnp_struct(padding, bool, int8, int16, int32, int64, uint8, uint16, uint32,
                   uint64, float32, float64, text):
    if pycapnp is None:
        pytest.skip('cannot import pycapnp')
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
    return pycapnp_schema.CapnpStruct.from_bytes(s.to_bytes())

@pytest.fixture(params=('instance', 'namedtuple', 'capnpy_', 'pycapnp'))
def Storage(request):
    p = request.param
    if p == 'instance':
        return Instance
    elif p == 'namedtuple':
        return NamedTuple
    elif p == 'capnpy_':
        return schema.CapnpStruct
    elif p == 'pycapnp':
        return pycapnp_struct
    else:
        raise NotImplementedError

# XXX: we should include bool as soon as it's supported by structor
@pytest.fixture(params=('int64', 'int8', 'int16', 'int32', 'uint8', 'uint16',
                        'uint32', 'uint64', 'float32', 'float64'))
def numeric_type(request):
    return request.param

class TestGetAttr(object):

    N = 2000

    @pytest.mark.benchmark(group="getattr")
    def test_getattr(self, Storage, numeric_type, benchmark):
        code = Code()
        code.global_scope.N = self.N
        code.global_scope.numeric_type = numeric_type
        code.ww("""
            def sum_attr(obj):
                myobjs = (obj, obj)
                res = 0
                for i in range({N}):
                    obj = myobjs[i%2]
                    res += obj.{numeric_type}
                return res
        """)
        code.compile()
        sum_attr = code['sum_attr']
        obj = Storage(padding=0, bool=100, int8=100, int16=100, int32=100, int64=100,
                      uint8=100, uint16=100, uint32=100, uint64=100, float32=100,
                      float64=100, text='some text')
        res = benchmark(sum_attr, obj)
        assert res == 100*self.N
