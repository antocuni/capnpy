import py
from capnpy.testing.compiler.support import CompilerTest
from capnpy.compiler import Compiler

class TestImport(CompilerTest):

    def test_load_schema_dont_load_twice(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
        }
        """
        mypkg = self.tmpdir.join("mypkg").ensure(dir=True)
        myschema = mypkg.join("myschema.capnp")
        myschema.write(schema)
        comp = Compiler([self.tmpdir], pyx=self.pyx)
        mod1 = comp.load_schema(modname="mypkg.myschema")
        mod2 = comp.load_schema(modname="mypkg.myschema")
        assert mod1 is mod2
        #
        mod3 = comp.load_schema(importname="/mypkg/myschema.capnp")
        assert mod3 is mod1
        #
        mod4 = comp.load_schema(filename=myschema)
        assert mod4 is mod1

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
        mod1 = comp.load_schema(importname="/tmp.capnp")
        mod2 = comp.load_schema(importname="/tmp.capnp")
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
        mod = comp.load_schema(importname="/tmp.capnp")

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
        mod = comp.load_schema(importname="/two/tmp.capnp")
