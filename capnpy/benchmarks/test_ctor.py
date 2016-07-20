import pytest
from pypytools.codegen import Code
from capnpy.benchmarks.test_benchmarks import schema

class TestCtor(object):

    N = 2000

    @pytest.mark.benchmark(group="ctor")
    def test_simple(self, schema, benchmark):
        code = Code()
        code.global_scope.N = self.N
        code.ww("""
            def new_and_sum(Point):
                res = 0
                for i in range({N}):
                    obj = Point(x=1, y=2, z=3)
                    res += obj.z
                return res
        """)
        code.compile()
        new_and_sum = code['new_and_sum']
        res = benchmark(new_and_sum, schema.Point)
        assert res == self.N*3
