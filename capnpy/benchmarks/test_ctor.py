import py
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

    BIG_TREE = py.path.local(__file__).dirpath('bigtree.dump')
    def _make_big_tree(self):
        from capnpy.benchmarks.support import Capnpy as schema
        def make(n):
            if n == 0:
                return None
            child = make(n-1)
            return schema.Node(x=9999, y=n, z=n,
                               left=child, right=child)
        tree = schema.Tree(make(12))
        with self.BIG_TREE.open('w') as f:
            tree.dump(f)
        print 'big tree wrote to ', self.BIG_TREE

    @pytest.mark.benchmark(group="copy_pointer")
    def test_copy_pointer(self, schema, benchmark):
        # this is similar to test_struct, but the struct we set has a very
        # deep structure, which means that we are effectively measuring the
        # performance of copy_pointer
        if schema.__name__ not in ('Capnpy', 'PyCapnp'):
            pytest.skip('N/A')
        #
        #self._make_big_tree() # uncomment this if you want to regenerate the file
        s = self.BIG_TREE.read()
        tree = schema.Tree.loads(s)

        def loop(oldtree):
            for i in range(1000):
                new_tree = schema.Tree(oldtree.root)
            return new_tree

        new_tree = benchmark(loop, tree)
        assert new_tree.root.x == 9999


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


    @pytest.mark.benchmark(group="ctor")
    def test_list_of_ints(self, schema, benchmark):
        code = Code()
        code.global_scope.N = self.N
        code.ww("""
            def new_and_sum(MyInt64List, items):
                res = 0
                for i in range({N}):
                    obj = MyInt64List(items)
                    res += 1
                return res
        """)
        code.compile()
        new_and_sum = code['new_and_sum']
        items = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        res = benchmark(new_and_sum, schema.MyInt64List, items)
        assert res == self.N
