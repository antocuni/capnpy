import py
import sys
import textwrap
from capnpy.testing.compiler.support import CompilerTest
from capnpy.compiler.compiler import DistutilsCompiler

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
