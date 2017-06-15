import sys
import os
from setuptools import setup, find_packages, Extension

try:
    import Cython
    if Cython.__version__ < '0.25':
        print ('WARNING: required cython>0.25, found %s. The .c files will '
               'NOT be regenerated' % Cython.__version__)
        raise ImportError
    from Cython.Build import cythonize
except ImportError:
    def cythonize(extensions, **kwargs):
        # dummy version of cythonize, for when Cython is not installed. This
        # works only if you install from an sdist package, which contains the
        # already-converted C files
        def cname(fname):
            fname = fname.replace('.pyx', '.c').replace('.py', '.c')
            if not os.path.exists(fname):
                print ('%s does not exist and Cython is not installed. '
                       'Please install Cython to regenerate it '
                       'automatically.' % fname)
                sys.exit(1)
            return fname
        #
        for ext in extensions:
            ext.sources = [cname(s) for s in ext.sources]
        return extensions

def get_cython_extensions():
    DEBUG = False # whether to compile files with -g
    files = ["capnpy/segment/base.pyx",
             "capnpy/segment/segment.py",
             "capnpy/segment/builder.pyx",
             "capnpy/blob.py",
             "capnpy/enum.py",
             "capnpy/visit.py",
             "capnpy/struct_.py",
             "capnpy/list.py",
             "capnpy/type.py",
             "capnpy/message.py",
             "capnpy/buffered.py",
             "capnpy/filelike.py",
             "capnpy/ptr.pyx",
             "capnpy/packing.pyx",
             "capnpy/_hash.pyx",
             "capnpy/_util.pyx",
    ]

    root_dir = os.path.abspath(os.path.dirname(__file__))
    capnpy_dir = os.path.join(root_dir, 'capnpy')

    def getext(fname):
        extname = fname.replace('/', '.').replace('.pyx', '').replace('.py', '')
        if DEBUG:
            extra_compile_args = ['-O0', '-g']
        else:
            extra_compile_args = ['-O3']
        return Extension(
            extname,
            [fname],
            include_dirs = [capnpy_dir],
            extra_compile_args = extra_compile_args,
        )
    return cythonize(map(getext, files), gdb_debug=DEBUG)

if hasattr(sys, 'pypy_version_info'):
    # on PyPy
    ext_modules = []
    extra_install_requires = []
else:
    USE_CYTHON = os.environ.get('USE_CYTHON', '1')
    USE_CYTHON = int(USE_CYTHON)
    if USE_CYTHON:
        ext_modules = get_cython_extensions()
        extra_install_requires = ['cython>=0.25']
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
      install_requires=['pypytools>=0.3.2', 'docopt'] + extra_install_requires,
      setup_requires=['setuptools_scm'],
      zip_safe=False,
      entry_points = {
          "distutils.setup_keywords": [
              "capnpy_options = capnpy.compiler.distutils:capnpy_options",
              "capnpy_schemas = capnpy.compiler.distutils:capnpy_schemas",
          ],
      }
)
