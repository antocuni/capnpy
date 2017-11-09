import py
import textwrap
import capnpy
from capnpy.testing.compiler.support import CompilerTest
from capnpy.compiler.compiler import DynamicCompiler

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
        comp = DynamicCompiler([self.tmpdir])
        mod1 = comp.load_schema(modname="mypkg.myschema", pyx=self.pyx)
        mod2 = comp.load_schema(modname="mypkg.myschema", pyx=self.pyx)
        assert mod1 is mod2
        #
        mod3 = comp.load_schema(importname="/mypkg/myschema.capnp",
                                pyx=self.pyx)
        assert mod3 is mod1
        #
        mod4 = comp.load_schema(filename=myschema, pyx=self.pyx)
        assert mod4 is mod1

    def test_import(self):
        comp = DynamicCompiler([self.tmpdir])
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
        mod_tmp = comp.load_schema(importname="/tmp.capnp", pyx=self.pyx)
        self.check_pyx(mod_tmp)
        self.check_pyx(mod_tmp._p_capnp)
        a = mod_tmp._p_capnp.Point(1, 2)
        b = mod_tmp._p_capnp.Point(3, 4)
        rec = mod_tmp.Rectangle(a, b)
        assert rec.b.x == 3

    def test_import_list(self):
        comp = DynamicCompiler([self.tmpdir])
        self.tmpdir.join("p.capnp").write("""
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
        }
        enum Color {
            blue @0;
            yellow @1;
        }
        """)
        self.tmpdir.join("tmp.capnp").write("""
        @0xbf5147cbbecf40c2;
        using P = import "/p.capnp";
        struct Rectangle {
            a @0 :List(P.Point);
            b @1 :List(P.Color);
        }
        """)
        mod_tmp = comp.load_schema(importname="/tmp.capnp", pyx=self.pyx)
        a = mod_tmp._p_capnp.Point(1, 2)
        b = mod_tmp._p_capnp.Point(3, 4)
        blue = mod_tmp._p_capnp.Color.blue
        yellow = mod_tmp._p_capnp.Color.yellow
        rec = mod_tmp.Rectangle(a=[a, b], b=[blue, yellow])
        assert rec.a[1].x == 3
        assert rec.b[1] == yellow == 1

    def test_import_enum(self):
        comp = DynamicCompiler([self.tmpdir])
        self.tmpdir.join("p.capnp").write("""
        @0xbf5147cbbecf40c1;
        enum Color {
            blue @0;
            yellow @1;
        }
        """)
        self.tmpdir.join("tmp.capnp").write("""
        @0xbf5147cbbecf40c2;
        using P = import "/p.capnp";
        struct Rectangle {
            x @0 :P.Color;
        }
        """)
        mod_tmp = comp.load_schema(importname="/tmp.capnp", pyx=self.pyx)
        blue = mod_tmp._p_capnp.Color.blue
        rec = mod_tmp.Rectangle(blue)
        assert rec.x == blue

    def test_import_absolute(self):
        one = self.tmpdir.join('one').ensure(dir=True)
        two = self.tmpdir.join('two').ensure(dir=True)

        comp = DynamicCompiler([self.tmpdir])
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
        mod = comp.load_schema(importname="/two/tmp.capnp", pyx=self.pyx)

    def test_extended(self, monkeypatch):
        myschema = self.tmpdir.join('myschema.capnp')
        myschema_extended = self.tmpdir.join('myschema_extended.py')

        comp = DynamicCompiler([self.tmpdir])
        myschema.write("""
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
        }
        """)
        myschema_extended.write(textwrap.dedent("""
        @Point.__extend__
        class Point:
            foo = 'foo'
            def x2(self):
                return self.x * 2
        """))
        #
        monkeypatch.setattr(capnpy, 'mycompiler', comp, raising=False)
        monkeypatch.syspath_prepend(self.tmpdir)
        mod = comp.load_schema('myschema', pyx=self.pyx)
        assert mod.Point.foo == 'foo'
        #
        p = mod.Point(5, 6)
        assert p.x == 5
        assert p.x2() == 10

    def test_unused_import(self):
        schema = """
        @0xbf5147cbbecf40c1;
        using Py = import "/capnpy/annotate.capnp";
        struct Empty {
        }
        """
        mod = self.compile(schema)
        assert not hasattr(mod, '_annotate_capnp')
