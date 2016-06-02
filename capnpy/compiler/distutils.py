from __future__ import absolute_import
import sys
import glob
import warnings
from distutils.core import Extension
from capnpy.compiler.compiler import DistutilsCompiler
try:
    from Cython.Build import cythonize
except ImportError:
    cythonize = None

# setuptools entry-points
def capnpy_options(dist, attr, value):
    my_options = set(['pyx', 'convert_case'])
    for opt in value:
        if opt not in my_options:
            warnings.warn('Unknown capnpy option: %s' % opt)

def capnpy_schemas(dist, attr, schemas):
    assert attr == 'capnpy_schemas'
    options = dist.capnpy_options or {}
    pyx = options.get('pyx', 'auto')
    convert_case = options.get('convert_case', True)
    if dist.ext_modules is None:
        dist.ext_modules = []
    dist.ext_modules += capnpify(schemas, pyx=pyx, convert_case=convert_case)

def capnpify(files, pyx='auto', convert_case=True):
    if isinstance(files, str):
        files = glob.glob(files)
        if files == []:
            raise ValueError("'%s' did not match any files" % files)
    compiler = DistutilsCompiler(sys.path)
    outfiles = [compiler.compile(f, convert_case, pyx) for f in files]
    #
    if compiler.getpyx(pyx):
        exts = []
        for f in outfiles:
            ext = Extension('*', [str(f)],
                            include_dirs=compiler.include_dirs)
            exts.append(ext)
        exts = cythonize(exts)
        return exts
    else:
        return []
