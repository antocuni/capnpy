from __future__ import absolute_import
import py
import sys
import glob
import warnings
from distutils.core import Extension
from capnpy.compiler.compiler import DistutilsCompiler
from capnpy import annotate
try:
    from Cython.Build import cythonize
except ImportError:
    cythonize = None

# setuptools entry-points
def capnpy_options(dist, attr, value):
    for opt in value:
        if opt != 'pyx' and opt not in annotate.Options.FIELDS:
            warnings.warn('Unknown capnpy option: %s' % opt)

def capnpy_schemas(dist, attr, schemas):
    assert attr == 'capnpy_schemas'
    option_dict = dist.capnpy_options or {}
    pyx = option_dict.pop('pyx', 'auto')
    options = annotate.Options.from_dict(option_dict)
    if dist.ext_modules is None:
        dist.ext_modules = []
    dist.ext_modules += capnpify(schemas, pyx, options)

def capnpify(files, pyx='auto', options=None):
    cwd = py.path.local('.')
    if isinstance(files, str):
        files = glob.glob(files)
        if files == []:
            raise ValueError("'%s' did not match any files" % files)
    compiler = DistutilsCompiler(sys.path)
    outfiles = [compiler.compile(f, pyx, options) for f in files]
    outfiles = [outf.relto(cwd) for outf in outfiles]
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
