import pytest
import pypytools
from collections import namedtuple
import capnpy
schema = capnpy.load_schema('/capnpy/benchmarks/point.capnp')

class points(object):
    capnpy = schema.Point
    namedtuple = namedtuple('Point', ['x', 'y'])

    @staticmethod
    def c_ext(x, y):
        if pypytools.is_pypy:
            pytest.skip('CPython only')
        import point
        pp = schema.Point(x=100, y=200)
        return point.Point(pp._buf, pp._offset)

@pytest.fixture(params=["namedtuple", "capnpy", "c_ext"])
def Point(request):
    return getattr(points, request.param)

def test_field(benchmark, Point):
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

