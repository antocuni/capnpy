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

class TestGetAttr(object):

    N = 2000

    @staticmethod
    def get_obj(schema):
        inner = schema.MyInner(field=200)
        obj = schema.MyStruct(padding=0, bool=100, int8=100, int16=100, int32=100,
                              int64=100, uint8=100, uint16=100, uint32=100, uint64=100,
                              float32=100, float64=100, text='hello world', group=(100,),
                              inner=inner, intlist=[1, 2, 3, 4])
        return obj

    @pytest.mark.benchmark(group="getattr")
    def test_numeric(self, schema, numeric_type, benchmark, obj=None):
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

    @pytest.mark.benchmark(group="getattr")
    def test_list(self, schema, benchmark):
        def sum_attr(obj):
            myobjs = (obj, obj)
            res = 0
            for i in range(self.N):
                obj = myobjs[i%2]
                res += obj.intlist[2]
            return res
        #
        obj = self.get_obj(schema)
        res = benchmark(sum_attr, obj)
        assert res == 3*self.N

    @pytest.mark.benchmark(group="getattr")
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

    @pytest.mark.benchmark(group="getattr")
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

    @pytest.mark.benchmark(group="getattr")
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


class TestMessage(object):

    N = 2000

    @pytest.mark.benchmark(group="getattr")
    def test_load(self, tmpdir, schema, benchmark):
        if not hasattr(schema.MyStruct, 'load'):
            py.test.skip('N/A')
        #
        def load_from_file(f):
            for i in range(self.N):
                f.seek(0)
                obj = schema.MyStruct.load(f)
            return obj
        #
        # we always create the object with capnpy, so that we can dumps() it.
        obj = TestGetAttr.get_obj(support.Capnpy)
        # we need to use a real file instead of cStringIO, because apparently
        # pycapnp cannot read from it
        tmpfile = tmpdir.join('mymessage')
        tmpfile.write(obj.dumps(), 'wb')
        with tmpfile.open() as f:
            res = benchmark(load_from_file, f)
        assert res.int64 == 100


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
        obj = schema.Point(1000, 2000, 3000)
        res = benchmark(self.hash_many, obj)
        assert res == 0

    @pytest.mark.benchmark(group="hash_int")
    def test_hash_ints_tuple(self, benchmark):
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
        obj = schema.StrPoint('hello world'[:], 'this is a string',
                              'this is another string')
        res = benchmark(self.hash_many, obj)
        assert res == 0

    @pytest.mark.benchmark(group="hash_str")
    def test_hash_str_tuple(self, benchmark):
        obj = ('hello world', 'this is a string', 'this is another string')
        res = benchmark(self.hash_many, obj)
        assert res == 0
