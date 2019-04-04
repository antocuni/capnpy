import py
from capnpy.testing.compiler.support import CompilerTest

class TestReflection(CompilerTest):

    def test___capnpy_id__(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
        }
        """
        mod = self.compile(schema)
        assert mod.__capnpy_id__ == 0xbf5147cbbecf40c1
        # we don't want to hardcode the exact value of Point's id, just check
        # that it exists
        assert mod.Point.__capnpy_id__
