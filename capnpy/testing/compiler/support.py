import py
import pytest
import textwrap
import capnpy
from capnpy.blob import PYX
from capnpy.compiler.compiler import DynamicCompiler


@pytest.mark.usefixtures('initargs')
class CompilerTest:
    """
    Base class for compiler tests: the initargs fixture ensures that:

        1. we have self.tmpdir available

        2. we have self.pyx set to True or False, depending whether we want to
           test the pure-python or cython compiler

    Both attributes are used by self.compile(), so that the final tests can
    simply call it without any further setup required.
    """

    SKIP = ()

    @pytest.fixture(params=['py', 'pyx'])
    def initargs(self, request, tmpdir):
        if request.param in self.SKIP:
            py.test.skip('%s tests disabled for this class' % request.param)
        #
        self.tmpdir = tmpdir
        self.pyx = request.param == 'pyx'
        if self.pyx and not request.config.option.pyx:
            py.test.skip('no pyx')
        if self.pyx and not PYX:
            py.test.skip('cannot test pyx if PYX==False')
        self.annotate = request.config.option.annotate

    def compile(self, s, **kwds):
        # root is needed to be able to import capnpy/py.capnp
        root = py.path.local(capnpy.__file__).dirpath('..')
        comp = DynamicCompiler([root, self.tmpdir], pyx=self.pyx)
        comp.annotate = self.annotate
        tmp_capnp = self.tmpdir.join('tmp.capnp')
        tmp_capnp.write(s)
        schema = comp.load_schema(importname='/tmp.capnp', **kwds)
        return schema

    def write(self, filename, src, **kwds):
        src = textwrap.dedent(src)
        filename = self.tmpdir.join(filename)
        if kwds:
            src = src.format(**kwds)
        filename.write(src)
        return filename
