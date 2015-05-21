import pytest
import pypytools
from collections import namedtuple
import capnpy
schema = capnpy.load_schema('/capnpy/benchmarks/point.capnp')

class points(object):
    capnpy = schema.Point
    namedtuple = namedtuple('Point', ['x', 'y'])

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

