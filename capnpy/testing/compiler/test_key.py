import py
import sys
from capnpy.testing.compiler.support import CompilerTest

class TestKey(CompilerTest):

    def test_key_on_struct(self):
        schema = """
        @0xbf5147cbbecf40c1;
        using Py = import "/capnpy/annotate.capnp";
        struct Point $Py.key("x, y") {
            x @0 :Int64;
            y @1 :Int64;
            name @2 :Text;
        }
        """
        mod = self.compile(schema)
        p1 = mod.Point(1, 2, "p1")
        p2 = mod.Point(1, 2, "p2")
        p3 = mod.Point(3, 4, "p3")
        assert p1 == p2
        assert p1 != p3
        #
        assert p1 == (1, 2)
        assert p3 == (3, 4)
        assert hash(p1) == hash(p2) == hash((1, 2))

    def test_key_convert_case(self):
        schema = """
        @0xbf5147cbbecf40c1;
        using Py = import "/capnpy/annotate.capnp";
        struct Foo $Py.key("fieldOne, fieldTwo") {
            fieldOne @0 :Int64;
            fieldTwo @1 :Int64;
        }
        """
        mod = self.compile(schema)
        p1 = mod.Foo(1, 2)
        assert p1 == (1, 2)
        assert hash(p1) == hash((1, 2))

    def test_key_on_group(self):
        schema = """
        @0xbf5147cbbecf40c1;
        using Py = import "/capnpy/annotate.capnp";
        struct Point {
            point :group $Py.key("x, y") {
                x @0 :Int64;
                y @1 :Int64;
            }
            name @2 :Text;
        }
        """
        mod = self.compile(schema)
        p1 = mod.Point((1, 2), "p1")
        p2 = mod.Point((1, 2), "p2")
        p3 = mod.Point((3, 4), "p3")
        assert p1.point == p2.point
        assert p1.point != p3.point
        #
        assert p1.point == (1, 2)
        assert p3.point == (3, 4)
        assert hash(p1.point) == hash(p2.point) == hash((1, 2))

    def test_wildcard(self):
        schema = """
        @0xbf5147cbbecf40c1;
        using Py = import "/capnpy/annotate.capnp";
        struct Point $Py.key("*") {
            x @0 :Int64;
            y @1 :Int64;
            name @2 :Text;
        }
        """
        mod = self.compile(schema)
        p1 = mod.Point(1, 2, "p1")
        p2 = mod.Point(1, 2, "p1")
        p3 = mod.Point(1, 2, "p3")
        assert p1 == p2
        assert p1 != p3
        #
        assert p1 == (1, 2, "p1")
        assert p3 == (1, 2, "p3")
        assert hash(p1) == hash(p2) == hash((1, 2, "p1"))



class TestFashHash(CompilerTest):

    SKIP = ('py',) # pyx only test

    def only_fasthash(self, cls):
        @cls.__extend__
        class Foo:
            def _key(self):
                raise ValueError('slow hash not allowed')

    def test_only_fasthash(self):
        # check that "only_fasthash" works as expected
        schema = """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
            name @2 :Text;
        }
        """
        mod = self.compile(schema)
        self.only_fasthash(mod.Point)
        p1 = mod.Point(1, 2, "p1")
        exc = py.test.raises(ValueError, "hash(p1)")
        assert str(exc.value) == "slow hash not allowed"

    def test_fasthash_int_long(self):
        schema = """
        @0xbf5147cbbecf40c1;
        using Py = import "/capnpy/annotate.capnp";
        struct Point $Py.key("x, y") {
            x @0 :Int64;
            y @1 :UInt64;
            name @2 :Text;
        }
        """
        mod = self.compile(schema)
        self.only_fasthash(mod.Point)
        p1 = mod.Point(1, sys.maxint+1, "p1")
        assert hash(p1) == hash((1, sys.maxint+1))

    def test_fasthash_string(self):
        schema = """
        @0xbf5147cbbecf40c1;
        using Py = import "/capnpy/annotate.capnp";
        struct Person $Py.key("name, surname") {
            name @0 :Text;
            surname @1 :Text;
        }
        """
        mod = self.compile(schema)
        self.only_fasthash(mod.Person)
        p = mod.Person("mickey", "mouse")
        assert hash(p) == hash(("mickey", "mouse"))
