import py
import sys
import capnpy
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
        comp = StandaloneCompiler(sys.path)
        comp.compile(infile, pyx=self.pyx)

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

    def test_pickle(self):
        import cPickle as pickle
        self.compile("mypoint.capnp", """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
        }
        """)
        mypoint = self.import_('mypoint')
        p1 = mypoint.Point(1, 2)
        for proto in (0, pickle.HIGHEST_PROTOCOL):
            s = pickle.dumps(p1, proto)
            p2 = pickle.loads(s)
            assert p2.x == 1
            assert p2.y == 2

    def test_pickle_list(self):
        import cPickle as pickle
        self.compile("example.capnp", """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
        }
        struct Foo {
            points @0 :List(Point);
            ints @1 :List(Int64);
        }
        """)
        mod = self.import_('example')
        p1 = mod.Point(1, 2)
        p2 = mod.Point(3, 4)
        f = mod.Foo(points=[p1, p2], ints=[1, 2, 3])
        for proto in (0, pickle.HIGHEST_PROTOCOL):
            s = pickle.dumps(f, proto)
            f2 = pickle.loads(s)
            assert f.points[0].x == 1
            assert f.points[0].y == 2
            assert f.points[1].x == 3
            assert f.points[1].y == 4
            assert f.ints == [1, 2, 3]
        #
        for proto in (0, pickle.HIGHEST_PROTOCOL):
            py.test.raises(TypeError, "pickle.dumps(f.points, proto)")
        #
        for proto in (0, pickle.HIGHEST_PROTOCOL):
            py.test.raises(TypeError, "pickle.dumps(f.ints, proto)")

    def test_version(self, monkeypatch):
        monkeypatch.setattr(capnpy, '__version__', 'fake 1.0')
        self.compile("example.capnp", """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0: Int64;
            y @1: Int64;
        }
        """)
        example = self.import_('example')
        assert example.__capnpy_version__ == 'fake 1.0'

    def test_version_check(self, monkeypatch):
        monkeypatch.setattr(capnpy, '__version__', 'Fake 1.0')
        self.compile("example.capnp", """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0: Int64;
            y @1: Int64;
        }
        """)
        monkeypatch.setattr(capnpy, '__version__', 'Fake 2.0')
        exc = py.test.raises(ImportError, "self.import_('example')")
        expected = ('Version mismatch: the module has been compiled with capnpy '
                    'Fake 1.0, but the current version of capnpy is Fake 2.0. '
                    'Please recompile.')
        assert str(exc.value) == expected


