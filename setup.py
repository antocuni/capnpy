import os
from setuptools import setup, find_packages, Extension

USE_CYTHON = int(os.environ.get('USE_CYTHON', '0'))

if USE_CYTHON:
    from Cython.Build import cythonize

    files = ["capnpy/blob.py",
             "capnpy/struct_.py",
             "capnpy/field.py",
             "capnpy/type.py",
             "capnpy/unpack.pyx",
             "capnpy/benchmarks/mypoint.pyx"]

    def getext(fname):
        extname = fname.replace('/', '.').replace('.pyx', '').replace('.py', '')
        return Extension(extname, [fname])

    ext_modules = cythonize(map(getext, files), gdb_debug=False)

else:
    ext_modules = []

setup(name="capnpy",
      version="0.1",
      packages = find_packages(),
      package_data = {
          'capnpy': ['*.capnp', '*.pyx']
          },
      ext_modules = ext_modules)
