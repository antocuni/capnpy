import py
import pytest
import sys
import os
from capnpy.testing.compiler.support import CompilerTest
from capnpy.compiler.compiler import DistutilsCompiler

@pytest.fixture
def ROOT():
    import pkg_resources
    try:
        dist = pkg_resources.get_distribution('capnpy')
    except pkg_resources.DistributionNotFound:
        raise ValueError("Cannot find the capnpy distribution: "
                         "please run setup.py install. "
                         "If you are running the tests from the checkout, "
                         "please run setup.py egg_info")
    #
    return py.path.local(dist.location)

class TestDistutilsCompiler(CompilerTest):

    def compile(self, filename):
        filename = self.tmpdir.join(filename)
        compiler = DistutilsCompiler([])
        return compiler.compile(filename, pyx=self.pyx)

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

    def test_setup_build(self, monkeypatch, ROOT):
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

    def test_setuptools_build(self, monkeypatch, ROOT):
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
        from setuptools import setup

        setup(name='foo',
              version='1.0',
              capnpy_options=dict(pyx={pyx}),
              capnpy_schemas=['example.capnp'],
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
