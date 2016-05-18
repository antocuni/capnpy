import py
import sys
from capnpy.testing.compiler.support import CompilerTest
from capnpy.compiler.compiler import StandaloneCompiler

class TestStandalone(CompilerTest):

    @py.test.fixture(params=['py', 'pyx'])
    def initargs(self, request, tmpdir, monkeypatch):
        CompilerTest.initargs(self, request, tmpdir)
        monkeypatch.syspath_prepend(tmpdir)
        self.imports = []

    def compile(self, filename, src):
        infile = self.write(filename, src.strip())
        comp = StandaloneCompiler(sys.path, pyx=self.pyx)
        comp.compile(infile)

    def import_(self, modname):
        mod = __import__(modname)
        self.imports.append(modname)
        return mod

    def teardown(self):
        # remove the modules which we have imported for the test from
        # sys.modules
        for modname in self.imports:
            del sys.modules[modname]

    def test_compile_and_import(self):
        self.compile("example.capnp", """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0: Int64;
            y @1: Int64;
        }
        """)
        example = self.import_('example')
        p = example.Point(x=1, y=2)

    def test_extended(self):
        self.compile("example.capnp", """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0: Int64;
            y @1: Int64;
        }
        """)
        self.write("example_extended.py", """
        @Point.__extend__
        class Point:
            foo = 'bar'
        """)
        example = self.import_('example')
        assert example.Point.foo == 'bar'

    def test_import_schema(self):
        self.compile("mypoint.capnp", """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
        }
        """)
        self.compile("myrect.capnp", """
        @0xbf5147cbbecf40c2;
        using P = import "/mypoint.capnp";
        struct Rectangle {
            a @0 :P.Point;
            b @1 :P.Point;
        }
        """)
        myrect = self.import_('myrect')
        mypoint = self.import_('mypoint')
        r = myrect.Rectangle(mypoint.Point(1, 2), mypoint.Point(3, 4))
        assert r.a.x == 1
        assert r.a.y == 2
        assert r.b.x == 3
        assert r.b.y == 4
