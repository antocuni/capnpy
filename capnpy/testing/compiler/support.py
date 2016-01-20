import py
import pytest
import capnpy
from capnpy.compiler import Compiler


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

    @pytest.fixture(params=['py', 'pyx'])
    def initargs(self, request, tmpdir):
        self.tmpdir = tmpdir
        self.pyx = request.param == 'pyx'
        if self.pyx and not request.config.option.pyx:
            py.test.skip('no pyx')

    def compile(self, s, **kwds):
        # root is needed to be able to import capnpy/py.capnp
        root = py.path.local(capnpy.__file__).dirpath('..')
        comp = Compiler([root, self.tmpdir], pyx=self.pyx)
        tmp_capnp = self.tmpdir.join('tmp.capnp')
        tmp_capnp.write(s)
        return comp.load_schema('/tmp.capnp', **kwds)

