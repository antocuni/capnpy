import py
import sys
import textwrap
from capnpy.testing.compiler.support import CompilerTest
from capnpy.compiler.compiler import StandaloneCompiler

#@py.test.mark.usefixtures('init')
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

    def write(self, filename, src):
        src = textwrap.dedent(src)
        filename = self.tmpdir.join(filename)
        filename.write(src)
        return filename

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
