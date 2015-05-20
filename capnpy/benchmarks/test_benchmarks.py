import pypytools
import time
import capnpy
from collections import namedtuple
import pytest

Point = namedtuple('Point', ['x', 'y'])
schema = capnpy.load_schema('/capnpy/benchmarks/point.capnp')

@pytest.mark.benchmark(group='Primitive field')
class TestPrimitiveField:

    N = 2000

    def do(self, p):
        res = 0
        for i in range(self.N):
            res += p.x
        return res

    def test_capnpy(self, benchmark):
        p = schema.Point(x=100, y=200)
        res = benchmark(self.do, p=p)
        assert res == 100*self.N

    def test_namedtuple(self, benchmark):
        p = Point(x=100, y=200)
        res = benchmark(self.do, p=p)
        assert res == 100*self.N
