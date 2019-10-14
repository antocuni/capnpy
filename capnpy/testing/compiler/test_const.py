import pytest
from capnpy.testing.compiler.support import CompilerTest

class TestConst(CompilerTest):

    def test_global_const(self):
        schema = """
        @0xbf5147cbbecf40c1;
        const bar :UInt16 = 42;
        const baz :Text = "baz";
        """
        mod = self.compile(schema)
        assert mod.bar == 42
        assert mod.baz == b'baz'

    def test_const_primitive(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            const bar :UInt16 = 42;
            const baz :Text = "baz";
        }
        """
        mod = self.compile(schema)
        assert mod.Foo.bar == 42
        assert mod.Foo.baz == b'baz'
