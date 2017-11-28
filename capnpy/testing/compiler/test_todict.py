from capnpy.testing.compiler.support import CompilerTest


class TestTodict(CompilerTest):
    def test_fields(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
        }
        """
        mod = self.compile(schema)
        assert mod.Point._fields == ('x', 'y')

    def test_todict(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
        }
        """
        mod = self.compile(schema)
        p = mod.Point(1, 2)
        d = p._asdict()
        assert d == {'x': 1, 'y': 2}
        assert list(d)[0] == 'x'

