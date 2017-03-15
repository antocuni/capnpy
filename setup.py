import sys
import os
from setuptools import setup, find_packages, Extension

try:
    import Cython
except ImportError:
    HAS_CYTHON = False
else:
    if Cython.__version__ >= '0.23':
        HAS_CYTHON = True
    else:
        HAS_CYTHON = False
        print 'WARNING: disabling Cython support, needed Cython >= 0.23'


USE_CYTHON = os.environ.get('USE_CYTHON', 'auto')
if USE_CYTHON == 'auto':
    is_pypy = hasattr(sys, 'pypy_version_info')
    USE_CYTHON = not is_pypy
else:
    USE_CYTHON = int(USE_CYTHON)

def get_cython_extensions():
    from Cython.Build import cythonize
    files = ["capnpy/blob.py",
             "capnpy/visit.py",
             "capnpy/struct_.py",
             "capnpy/list.py",
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

# we try to cythonize() the files even if USE_CYTHON is False; this way, we
# make sure that the *.c files will be included in the sdist. This is needed
# so that people (and tox!) can download the sdist and build the extensions
# *without* having cython installed
if HAS_CYTHON:
    cython_modules = get_cython_extensions()
else:
    cython_modules = []
#
if USE_CYTHON:
    ext_modules = cython_modules
else:
    ext_modules = []


setup(name="capnpy",
      author='Antonio Cuni',
      author_email='anto.cuni@gmail.com',
      url='https://bitbucket.org/antocuni/capnpy',
      use_scm_version=True,
      include_package_data=True,
      packages = find_packages(),
      ext_modules = ext_modules,
      install_requires=['pypytools>=0.3', 'docopt'],
      setup_requires=['setuptools_scm'],
      zip_safe=False,
      entry_points = {
          "distutils.setup_keywords": [
              "capnpy_options = capnpy.compiler.distutils:capnpy_options",
              "capnpy_schemas = capnpy.compiler.distutils:capnpy_schemas",
          ],
      }
)
