import py
import sys
from capnpy.testing.compiler.support import CompilerTest
import capnpy

class TestPyGroup(CompilerTest):

    def test_access(self):
        schema = """
        @0xbf5147cbbecf40c1;
        using Py = import "/capnpy/annotate.capnp";
        struct Foo {
            s @0 :Int64;
            x @1 :Int64;
            y @2 :Int64;
            z @3 :Text;
            xyz @4: Void $Py.group("x, y, z");
        }
        """
        mod = self.compile(schema)
        foo = mod.Foo(1, 2, 3, b'abc')
        foo2 = capnpy.loads(foo.dumps(), mod.Foo)
        assert foo.s == foo2.s == 1
        assert foo.x == foo.xyz.x == foo2.x == foo2.xyz.x == 2
        assert foo.y == foo.xyz.y == foo2.y == foo2.xyz.y == 3
        assert foo.z == foo.xyz.z == foo2.z == foo2.xyz.z == b'abc'

    def test_key(self):
        schema = """
        @0xbf5147cbbecf40c1;
        using Py = import "/capnpy/annotate.capnp";
        struct Foo {
            s @0 :Int64;
            x @1 :Int64;
            y @2 :Int64;
            z @3 :Text;
            xyz @4: Void $Py.group("x, y, z") $Py.key("x, z");
        }
        """
        mod = self.compile(schema)
        foo = mod.Foo(1, 2, 3, b'abc')
        foo2 = capnpy.loads(foo.dumps(), mod.Foo)
        assert hash(foo.s) == hash(foo2.s) == 1
        assert foo.xyz == foo2.xyz == (foo.x, foo.z) == (2, b'abc')
        assert hash(foo.xyz) == hash(foo2.xyz) == hash((foo.x, foo.z)) == hash((2, b'abc'))

    def test_key_star(self):
        schema = """
        @0xbf5147cbbecf40c1;
        using Py = import "/capnpy/annotate.capnp";
        struct Foo {
            s @0 :Int64;
            x @1 :Int64;
            y @2 :Int64;
            z @3 :Text;
            xyz @4: Void $Py.group("x, y, z") $Py.key("*");
        }
        """
        mod = self.compile(schema)
        foo = mod.Foo(1, 2, 3, b'abc')
        foo2 = capnpy.loads(foo.dumps(), mod.Foo)
        assert hash(foo.s) == hash(foo2.s) == 1
        assert foo.xyz == foo2.xyz == (foo.x, foo.y, foo.z) == (2, 3, b'abc')
        assert hash(foo.xyz) == hash(foo2.xyz) == hash((foo.x, foo.y, foo.z)) == hash((2, 3, b'abc'))

