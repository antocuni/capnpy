from __future__ import absolute_import
import sys
import glob
from distutils.core import Extension
from capnpy.compiler.compiler import DistutilsCompiler
try:
    from Cython.Build import cythonize
except ImportError:
    cythonize = None

def capnpify(files, pyx='auto', convert_case=True):
    if isinstance(files, str):
        files = glob.glob(files)
        if files == []:
            raise ValueError("'%s' did not match any files" % files)
    compiler = DistutilsCompiler(sys.path, pyx=pyx)
    outfiles = [compiler.compile(f, convert_case) for f in files]
    #
    if compiler.pyx:
        exts = []
        for f in outfiles:
            ext = Extension('*', [str(f)],
                            include_dirs=compiler.include_dirs)
            exts.append(ext)
        exts = cythonize(exts)
        return exts
    else:
        return []
