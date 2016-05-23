import py
import sys
import os
from capnpy.testing.compiler.support import CompilerTest
from capnpy.compiler.compiler import DistutilsCompiler, PKGDIR

class TestDistutilsCompiler(CompilerTest):

    def compile(self, filename):
        filename = self.tmpdir.join(filename)
        compiler = DistutilsCompiler([], pyx=self.pyx)
        return compiler.compile(filename)

    def test_simple(self):
        self.write("example.capnp", """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0: Int64;
            y @1: Int64;
        }
        """)
        outfile = self.compile("example.capnp")
        assert outfile.exists()
        if self.pyx:
            assert outfile == self.tmpdir.join('example.pyx')
        else:
            assert outfile == self.tmpdir.join('example.py')

    def test_dont_compile_if_newer(self):
        self.write("example.capnp", """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0: Int64;
            y @1: Int64;
        }
        """)
        outfile = self.compile("example.capnp")
        mtime = outfile.mtime()
        outfile2 = self.compile("example.capnp")
        assert outfile == outfile2
        assert outfile2.mtime() == mtime
        #
        infile = self.tmpdir.join("example.capnp")
        infile.setmtime(mtime+1)
        #
        outfile3 = self.compile("example.capnp")
        assert outfile == outfile3
        assert outfile3.mtime() > mtime


class TestSetup(CompilerTest):

    def test_setup_build(self, monkeypatch):
        ROOT = PKGDIR.dirpath()
        self.write("example.capnp", """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0: Int64;
            y @1: Int64;
        }
        """)
        self.write("setup.py", """
        import sys
        sys.path.insert(0, '{root}')
        from distutils.core import setup
        from capnpy.compiler.distutils import capnpify

        exts = capnpify("*.capnp", pyx={pyx})
        setup(name='foo',
              version='1.0',
              ext_modules = exts,
              )
        """, root=ROOT, pyx=self.pyx)
        #
        monkeypatch.chdir(self.tmpdir)
        ret = os.system('%s setup.py build_ext --inplace' % sys.executable)
        assert ret == 0
        if self.pyx:
            outfile = self.tmpdir.join('example.so')
        else:
            outfile = self.tmpdir.join('example.py')
        #
        assert outfile.check(file=True)