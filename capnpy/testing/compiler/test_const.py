import pytest
import capnpy
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

    def test_struct(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Person {
            name @0 :Text;
            email @1 :Text;
        }
        const bob :Person = (name = "Bob", email = "bob@example.com");
        """
        mod = self.compile(schema)
        assert mod.bob.name == b'Bob'
        assert mod.bob.email == b'bob@example.com'
        #
        # check that reflection data and constants share the same segment
        reflection = capnpy.get_reflection_data(mod)
        assert reflection.request._seg is mod.bob._seg

    def test_list(self):
        schema = """
        @0xbf5147cbbecf40c1;
        const int64List :List(Int64) = [1, 2, 3, 4];
        const textList :List(Text) = ["hello", "world"];
        """
        mod = self.compile(schema)
        assert mod.int64List == [1, 2, 3, 4]
        assert mod.textList == [b'hello', b'world']

    def test_struct_no_reflection(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Person {
            name @0 :Text;
            email @1 :Text;
        }
        const bob :Person = (name = "Bob", email = "bob@example.com");
        """
        # check that we can emit the const even if we don't have the
        # reflection data
        mod = self.compile(schema, include_reflection_data=False)
        assert mod.bob.name == b'Bob'
        assert mod.bob.email == b'bob@example.com'
