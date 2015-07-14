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
        myschema = capnp.load('point.capnp')
        p = myschema.Point.new_message()
        p.x = x
        p.y = y
        return myschema.Point.from_bytes(p.to_bytes())


@pytest.fixture(params=[key for key in vars(points) if key[0] != '_'])
def Point(request):
    return getattr(points, request.param)

@pytest.mark.benchmark(group="getattr")
def test_getattr(benchmark, Point):
    N = 2000
    @pypytools.clonefunc
    def sum_xs(p):
        res = 0
        for i in range(N):
            res += p.x
        return res
    #
    p = Point(x=100, y=200)
    res = benchmark(sum_xs, p)
    assert res == 100*N

