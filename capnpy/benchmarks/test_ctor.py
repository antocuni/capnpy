import pytest
from pypytools.codegen import Code
from capnpy.benchmarks.test_benchmarks import schema, get_obj

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


    @pytest.mark.benchmark(group="ctor")
    def test_text(self, schema, benchmark):
        code = Code()
        code.global_scope.N = self.N
        code.ww("""
            def new_and_sum(StrPoint):
                res = 0
                for i in range({N}):
                    obj = StrPoint(x='hello',
                                   y='this is a longer string',
                                   z='bar')
                    res += len(obj.z)
                return res
        """)
        code.compile()
        new_and_sum = code['new_and_sum']
        res = benchmark(new_and_sum, schema.StrPoint)
        assert res == self.N*3


    @pytest.mark.benchmark(group="ctor")
    def test_struct(self, schema, benchmark):
        code = Code()
        code.global_scope.N = self.N
        code.ww("""
            def new_and_sum(Rectangle, a, b):
                res = 0
                for i in range({N}):
                    obj = Rectangle(a=a, b=b)
                    res += 1
                return res
        """)
        code.compile()
        new_and_sum = code['new_and_sum']
        a = schema.Point(1, 2, 3)
        b = schema.Point(4, 5, 6)
        res = benchmark(new_and_sum, schema.Rectangle, a, b)
        assert res == self.N


    @pytest.mark.benchmark(group="ctor")
    def test_list(self, schema, benchmark):
        code = Code()
        code.global_scope.N = self.N
        code.ww("""
            def new_and_sum(MyStructContainer, items):
                res = 0
                for i in range({N}):
                    obj = MyStructContainer(items)
                    res += 1
                return res
        """)
        code.compile()
        new_and_sum = code['new_and_sum']
        items = [get_obj(schema)] * 10
        res = benchmark(new_and_sum, schema.MyStructContainer, items)
        assert res == self.N
        ## import vmprof
        ## with open('/tmp/pytest.vmprof', 'w+') as f:
        ##     vmprof.enable(f.fileno(), native=True)
        ##     res = benchmark(new_and_sum, schema.MyStructContainer, items)
        ##     vmprof.disable()
