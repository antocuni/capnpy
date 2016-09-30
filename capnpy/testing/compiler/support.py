import py
import pytest
import textwrap
import capnpy
from capnpy.blob import PYX
from capnpy.compiler.compiler import DynamicCompiler, BaseCompiler


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
        comp = DynamicCompiler([root, self.tmpdir])
        comp.annotate = self.annotate
        tmp_capnp = self.tmpdir.join('tmp.capnp')
        tmp_capnp.write(s)
        schema = comp.load_schema(importname='/tmp.capnp', pyx=self.pyx,
                                  **kwds)
        return schema

    def getm(self, s, **kwds):
        comp = BaseCompiler([self.tmpdir])
        tmp_capnp = self.tmpdir.join('tmp.capnp')
        tmp_capnp.write(s)
        m, src = comp.generate_py_source(tmp_capnp, convert_case=True,
                                         pyx=self.pyx)
        return m

    def write(self, filename, src, **kwds):
        src = textwrap.dedent(src)
        filename = self.tmpdir.join(filename)
        if kwds:
            src = src.format(**kwds)
        filename.write(src)
        return filename

    def check_pyx(self, mod):
        if self.pyx:
            assert mod.__file__.endswith('.so')
            assert 'capnpy.ext' in mod.__name__
        else:
            assert mod.__file__.endswith('.capnp')
            assert 'capnpy.ext' not in mod.__name__
