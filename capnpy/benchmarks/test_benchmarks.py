import py
import pytest
import pypytools
from pypytools.codegen import Code
from capnpy.benchmarks import support

@pytest.fixture(params=('Instance', 'NamedTuple', 'Capnpy', 'PyCapnp'))
def schema(request):
    p = request.param
    return getattr(support, p)

# XXX: we should include bool as soon as it's supported by structor
@pytest.fixture(params=('int64', 'int8', 'int16', 'int32', 'uint8', 'uint16',
                        'uint32', 'uint64', 'float32', 'float64', 'group.field'))
def numeric_type(request):
    return request.param

class TestGetAttr(object):

    N = 2000

    def get_obj(self, schema):
        inner = schema.MyInner(field=200)
        obj = schema.MyStruct(padding=0, bool=100, int8=100, int16=100, int32=100,
                              int64=100, uint8=100, uint16=100, uint32=100, uint64=100,
                              float32=100, float64=100, text='some text', group=(100,),
                              inner=inner)
        return obj

    @pytest.mark.benchmark(group="getattr")
    def test_numeric(self, schema, numeric_type, benchmark):
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
        obj = self.get_obj(schema)
        res = benchmark(sum_attr, obj)
        assert res == 100*self.N

    @pytest.mark.benchmark(group="getattr")
    def test_text(self, schema, benchmark):
        def count_text(obj):
            myobjs = (obj, obj)
            res = 0
            for i in range(self.N):
                obj = myobjs[i%2]
                res += (obj.text == 'hello world')
            return res
        #
        obj = self.get_obj(schema)
        res = benchmark(count_text, obj)
        assert res == self.N

    @pytest.mark.benchmark(group="getattr")
    def test_struct(self, schema, benchmark):
        def sum_attr(obj):
            myobjs = (obj, obj)
            res = 0
            for i in range(self.N):
                obj = myobjs[i%2]
                res += obj.inner.field
            return res
        #
        obj = self.get_obj(schema)
        res = benchmark(sum_attr, obj)
        assert res == 200*self.N

