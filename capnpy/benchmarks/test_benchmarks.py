import py
import pytest
import pypytools
from collections import namedtuple
import capnpy

schema = capnpy.load_schema('/capnpy/benchmarks/point.capnp')
        
@pytest.fixture(params=[1, 2, 3])
def n(request):
    return request.param

class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

class points(object):
    namedtuple = namedtuple('Point', ['x', 'y'])
    capnpyx = schema.Point
    instance = Point

    @staticmethod
    def pycapnp(x, y):
        if pypytools.is_pypy:
            pytest.skip('CPython only')
        import capnp
        thisdir = py.path.local(__file__).dirpath()
        myschema = capnp.load(str(thisdir.join('point.capnp')))
        p = myschema.Point.new_message()
        p.x = x
        p.y = y
        return myschema.Point.from_bytes(p.to_bytes())


@pytest.fixture(params=[key for key in vars(points) if key[0] != '_'])
def Point(request):
    return getattr(points, request.param)

class TestGetAttr(object):

    N = 2000

    @pytest.mark.benchmark(group="getattr")
    def test_unpack_primitive(self, benchmark):
        """
        Measure the raw performance of unpack_primitive, i.e. how fast we can
        unpack Python strings into int64
        """
        import struct
        from capnpy.unpack import unpack_primitive
        #
        def sum_xs(buf):
            res = 0
            for i in range(self.N):
                res += unpack_primitive('q', buf, 0)
            return res
        #
        buf = struct.pack('q', 100)
        res = benchmark(sum_xs, buf)
        assert res == 100*self.N

    @pytest.mark.benchmark(group="getattr")
    def test__read_primitive(self, benchmark):
        from capnpy.blob import Types
        def sum_xs(p):
            int64 = Types.int64
            res = 0
            for i in range(self.N):
                res += p._read_primitive(0, int64)
            return res
        #
        p = schema.Point(x=100, y=200)
        res = benchmark(sum_xs, p)
        assert res == 100*self.N


    @pytest.mark.benchmark(group="getattr")
    def test_getattr(self, benchmark, Point):
        @pypytools.clonefunc
        def sum_xs(p):
            res = 0
            for i in range(self.N):
                res += p.x
            return res
        #
        p = Point(x=100, y=200)
        res = benchmark(sum_xs, p)
        assert res == 100*self.N

    @pytest.mark.benchmark(group="getattr")
    def test_cython_property(self, benchmark):
        @pypytools.clonefunc
        def sum_xs(p):
            res = 0
            for i in range(self.N):
                res += p.x
            return res
        #
        import struct
        from capnpy.benchmarks.mypoint import MyPoint
        buf = struct.pack('qq', 100, 200)
        p = MyPoint.from_buffer(buf, 0, None)
        assert p.x == 100
        assert p.y == 200
        res = benchmark(sum_xs, p)
        #assert res == 100*self.N
