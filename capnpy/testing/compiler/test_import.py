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
        mod = comp.load_schema(importname="/tmp.capnp", pyx=self.pyx)
        self.check_pyx(mod)
        self.check_pyx(mod._p_capnp)

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
