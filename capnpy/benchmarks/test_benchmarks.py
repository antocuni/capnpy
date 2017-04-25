import py
import pytest
import pypytools
from pypytools.codegen import Code
from capnpy.benchmarks import support

@pytest.fixture(params=('Instance', 'NamedTuple', 'Capnpy', 'PyCapnp'))
def schema(request):
    p = request.param
    res = getattr(support, p)
    res.__name__ = p
    return res

# XXX: we should include bool as soon as it's supported by structor
@pytest.fixture(params=('int64', 'int8', 'int16', 'int32', 'uint8', 'uint16',
                        'uint32', 'uint64', 'float32', 'float64', 'group.field'))
def numeric_type(request):
    return request.param

def get_obj(schema):
    inner = schema.MyInner(field=200)
    obj = schema.MyStruct(padding=0, bool=100, int8=100, int16=100, int32=100,
                          int64=100, uint8=100, uint16=100, uint32=100, uint64=100,
                          float32=100, float64=100, text='hello world', group=(100,),
                          inner=inner, intlist=[1, 2, 3, 4], color=2)
    return obj



class TestGetAttr(object):

    N = 2000

    @pytest.mark.benchmark(group="getattr")
    def test_numeric(self, schema, numeric_type, benchmark, obj=None):
        # the extra_info is used to generate the charts
        benchmark.extra_info['attribute_type'] = numeric_type
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
        obj = get_obj(schema)
        res = benchmark(sum_attr, obj)
        assert res == 100*self.N

    @pytest.mark.benchmark(group="getattr")
    def test_text(self, schema, benchmark):
        benchmark.extra_info['attribute_type'] = 'text'
        def count_text(obj):
            myobjs = (obj, obj)
            res = 0
            for i in range(self.N):
                obj = myobjs[i%2]
                res += (obj.text == 'hello world')
            return res
        #
        obj = get_obj(schema)
        res = benchmark(count_text, obj)
        assert res == self.N

    @pytest.mark.benchmark(group="getattr")
    def test_struct(self, schema, benchmark):
        benchmark.extra_info['attribute_type'] = 'struct'
        def sum_attr(obj):
            myobjs = (obj, obj)
            res = 0
            for i in range(self.N):
                obj = myobjs[i%2]
                res += obj.inner.field
            return res
        #
        obj = get_obj(schema)
        res = benchmark(sum_attr, obj)
        assert res == 200*self.N

    @pytest.mark.benchmark(group="getattr")
    def test_list(self, schema, benchmark):
        # mesaure the time to get the list field *AND* to compute the len
        benchmark.extra_info['attribute_type'] = 'list'
        def sum_attr(obj):
            myobjs = (obj, obj)
            res = 0
            for i in range(self.N):
                obj = myobjs[i%2]
                res += len(obj.intlist)
            return res
        #
        obj = get_obj(schema)
        res = benchmark(sum_attr, obj)
        assert res == 4*self.N

    @pytest.mark.benchmark(group="getattr")
    def test_enum(self, schema, benchmark):
        if schema.__name__ == 'PyCapnp':
            py.test.skip('broken')

        benchmark.extra_info['attribute_type'] = 'enum'
        def count_enum(obj):
            myobjs = (obj, obj)
            res = 0
            for i in range(self.N):
                obj = myobjs[i%2]
                res += obj.color
            return res
        #
        obj = get_obj(schema)
        res = benchmark(count_enum, obj)
        assert res == self.N*2


class TestGetAttrSpecial(object):
    N = 2000

    @pytest.mark.benchmark(group="getattr_special")
    def test_which(self, schema, benchmark):
        if schema.__name__ != 'Capnpy':
            py.test.skip('N/A')
        #
        def sum_which(obj):
            myobjs = (obj, obj)
            res = 0
            for i in range(self.N):
                obj = myobjs[i%2]
                res += obj.which()
            return res
        #
        obj = schema.WithUnion.new_two(42)
        res = benchmark(sum_which, obj)
        assert res == self.N*2

    @pytest.mark.benchmark(group="getattr_special")
    def test___which__(self, schema, benchmark):
        if schema.__name__ != 'Capnpy':
            py.test.skip('N/A')
        #
        def sum_which(obj):
            myobjs = (obj, obj)
            res = 0
            for i in range(self.N):
                obj = myobjs[i%2]
                res += obj.__which__()
            return res
        #
        obj = schema.WithUnion.new_two(42)
        res = benchmark(sum_which, obj)
        assert res == self.N*2

    @pytest.mark.benchmark(group="getattr_special")
    def test_is_union(self, schema, benchmark):
        if schema.__name__ != 'Capnpy':
            py.test.skip('N/A')
        #
        def sum_is(obj):
            myobjs = (obj, obj)
            res = 0
            for i in range(self.N):
                obj = myobjs[i%2]
                res += obj.is_two()
            return res
        #
        obj = schema.WithUnion.new_two(42)
        res = benchmark(sum_is, obj)
        assert res == self.N


class TestHash(object):

    N = 2000

    @classmethod
    def hash_many(cls, obj):
        myobjs = (obj, obj)
        res = 0
        for i in range(cls.N):
            obj = myobjs[i%2]
            res ^= hash(obj)
        return res

    @pytest.mark.benchmark(group="hash_int")
    def test_hash_ints(self, schema, benchmark):
        if schema.__name__ == 'PyCapnp':
            py.test.skip('pycapnp does not implement hash properly')
        benchmark.extra_info['schema'] = schema.__name__
        benchmark.extra_info['type'] = 'int64'
        obj = schema.Point(1000, 2000, 3000)
        res = benchmark(self.hash_many, obj)
        assert res == 0

    @pytest.mark.benchmark(group="hash_int")
    def test_hash_ints_tuple(self, benchmark):
        benchmark.extra_info['schema'] = 'tuple'
        benchmark.extra_info['type'] = 'int64'
        obj = (1000, 2000, 3000)
        res = benchmark(self.hash_many, obj)
        assert res == 0

    @pytest.mark.benchmark(group="hash_str")
    def test_hash_str(self, schema, benchmark):
        # This benchmark is particularly bad/hard for capnpy because we don't
        # cache the computed hash, as plain <str> objects do, hence we have to
        # compute it every time.
        if schema.__name__ == 'PyCapnp':
            py.test.skip('pycapnp does not implement hash properly')
        benchmark.extra_info['schema'] = schema.__name__
        benchmark.extra_info['type'] = 'str'
        obj = schema.StrPoint('hello world'[:], 'this is a string',
                              'this is another string')
        res = benchmark(self.hash_many, obj)
        assert res == 0

    @pytest.mark.benchmark(group="hash_str")
    def test_hash_str_tuple(self, benchmark):
        benchmark.extra_info['schema'] = 'tuple'
        benchmark.extra_info['type'] = 'str'
        obj = ('hello world', 'this is a string', 'this is another string')
        res = benchmark(self.hash_many, obj)
        assert res == 0


class TestList(object):
    """
    Contrarily to TestGetAttr.test_list, these tests do NOT measure the time
    taken to read a list field, but the time taken to do something with the
    list *after* we read it
    """

    N = 2000

    @pytest.mark.benchmark(group="list")
    def test_len(self, schema, benchmark):
        def mybench(obj):
            mylists = (obj.intlist, obj.intlist)
            res = 0
            for i in range(self.N):
                lst = mylists[i%2]
                res += len(lst)
            return res
        #
        obj = get_obj(schema)
        res = benchmark(mybench, obj)
        assert res == 4*self.N

    @pytest.mark.benchmark(group="list")
    def test_getitem(self, schema, benchmark):
        def mybench(obj):
            mylists = (obj.intlist, obj.intlist)
            res = 0
            for i in range(self.N):
                lst = mylists[i%2]
                res += lst[2]
            return res
        #
        obj = get_obj(schema)
        res = benchmark(mybench, obj)
        assert res == 3*self.N

    @pytest.mark.benchmark(group="list")
    def test_iter(self, schema, benchmark):
        # mesaure ONLY the time to iterate over a list
        def mybench(obj):
            mylists = (obj.intlist, obj.intlist)
            res = 0
            for i in range(self.N):
                lst = mylists[i%2]
                for item in lst:
                    res += item
            return res
        #
        obj = get_obj(schema)
        res = benchmark(mybench, obj)
        assert res == (4+3+2+1)*self.N
