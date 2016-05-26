import sys
import os
from setuptools import setup, find_packages, Extension

try:
    import Cython
except ImportError:
    HAS_CYTHON = False
else:
    HAS_CYTHON = True

USE_CYTHON = os.environ.get('USE_CYTHON', 'auto')
if USE_CYTHON == 'auto':
    is_pypy = hasattr(sys, 'pypy_version_info')
    USE_CYTHON = not is_pypy
else:
    USE_CYTHON = int(USE_CYTHON)

def get_cython_extensions():
    from Cython.Build import cythonize
    files = ["capnpy/blob.py",
             "capnpy/struct_.py",
             "capnpy/type.py",
             "capnpy/message.py",
             "capnpy/buffered.py",
             "capnpy/filelike.py",
             "capnpy/ptr.pyx",
             "capnpy/unpack.pyx",
             "capnpy/_hash.pyx",
             "capnpy/_util.pyx",
    ]

    def getext(fname):
        extname = fname.replace('/', '.').replace('.pyx', '').replace('.py', '')
        return Extension(
            extname,
            [fname],
            extra_compile_args = ['-O3'],
        )
    return cythonize(map(getext, files), gdb_debug=False)


ext_modules = []
if USE_CYTHON and HAS_CYTHON:
    ext_modules = get_cython_extensions()

setup(name="capnpy",
      author='Antonio Cuni',
      author_email='anto.cuni@gmail.com',
      url='https://bitbucket.org/antocuni/capnpy',
      use_scm_version=True,
      packages = find_packages(),
      package_data = {
          'capnpy': ['*.capnp', '*.pyx']
          },
      ext_modules = ext_modules,
      install_requires=['pypytools'],
      setup_requires=['setuptools_scm'],
      entry_points = {
          "distutils.setup_keywords": [
              "capnpy_options = capnpy.compiler.distutils:capnpy_options",
              "capnpy_schemas = capnpy.compiler.distutils:capnpy_schemas",
          ],
      }
)
