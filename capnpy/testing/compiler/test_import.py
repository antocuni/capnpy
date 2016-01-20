import py
from capnpy.testing.compiler.support import CompilerTest
from capnpy.compiler import Compiler

class TestImport(CompilerTest):

    def test_dont_load_twice(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
        }
        """
        self.tmpdir.join("tmp.capnp").write(schema)
        comp = Compiler([self.tmpdir], pyx=self.pyx)
        mod1 = comp.load_schema("/tmp.capnp")
        mod2 = comp.load_schema("/tmp.capnp")
        assert mod1 is mod2


    def test_import(self):
        comp = Compiler([self.tmpdir], pyx=self.pyx)
        self.tmpdir.join("p.capnp").write("""
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
        }
        """)
        self.tmpdir.join("tmp.capnp").write("""
        @0xbf5147cbbecf40c2;
        using P = import "/p.capnp";
        struct Rectangle {
            a @0 :P.Point;
            b @1 :P.Point;
        }
        """)
        mod = comp.load_schema("/tmp.capnp")

    def test_import_absolute(self):
        one = self.tmpdir.join('one').ensure(dir=True)
        two = self.tmpdir.join('two').ensure(dir=True)

        comp = Compiler([self.tmpdir], pyx=self.pyx)
        one.join("p.capnp").write("""
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
        }
        """)
        two.join("tmp.capnp").write("""
        @0xbf5147cbbecf40c2;
        using P = import "/one/p.capnp";
            struct Rectangle {
            a @0 :P.Point;
            b @1 :P.Point;
        }
        """)
        mod = comp.load_schema("/two/tmp.capnp")
