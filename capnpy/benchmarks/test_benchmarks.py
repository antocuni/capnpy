import py
import pytest
import pypytools
from pypytools.codegen import Code
import capnpy
from capnpy.benchmarks.support import Instance, NamedTuple, pycapnp_struct, NamedTuple_Group

schema = capnpy.load_schema('capnpy.benchmarks.benchmarks')


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
                        'uint32', 'uint64', 'float32', 'float64', 'group.field'))
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
                      float64=100, text='some text', group=(100,))
        res = benchmark(sum_attr, obj)
        assert res == 100*self.N
