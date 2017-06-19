import sys
import os
from setuptools import setup, find_packages, Extension
from setuptools.command.sdist import sdist
try:
    from Cython.Distutils import build_ext
except ImportError:
    from setuptools.command.build_ext import build_ext

"""
In the following, we speak about Cython being required or not: we are
talking about "setup.py-time requirements", i.e. if Cython needs to be
installed **before** trying to install capnpy.  Once the setup.py is running,
Cython will always be installed transparently because it's listed in
`install_requires`.

The following applies only to CPython; Cython is never required on PyPy.

There are various use-cases to consider:

  1. manual `setup.py sdist`: the custom command my_sdist make sure to
     generate the C files and include them in the .tar.gz. Cython is REQUIRED.

  2. manual install from the sdist tarball: it will use already-generated C
     files. Cython is NOT required.

  3. manual install from a git checkout: the C files will NOT be there; the
     custom command my_build_ext will take care of generate them
     automatically. Cython is REQUIRED.

  4. 'pip install capnpy': in most cases it will download a prebuilt binary
     wheel from pypi; in the others, it will build from the sdist. In both
     cases, Cython is NOT required.

  5. 'pip install git+http://github.com/...': pip will first install Cython
     (because it's in install_requires), then install capnpy (and since Cython
     is installed, the C files will be automatically generated). Thus, Cython
     is handled completely transparently.

So, Cython is handled transparently in cases (4) and (5), which are the two
most common ones.

In theory, we could add 'cython>=0.25' to setup_requires. This way, Cython
will be handled transparently also in the remaining cases. However:

  - if we do this setuptools tries to install cython in *all* cases

  - this installation is done by setuptools/easy_install, NOT pip

  - setuptools does not support installing from wheels; the result is that it
    tries to compile Cython, which is slow

  - this make cases (4) and (5) considerably slower than needed, because pip
    will be forced to wait for setuptools to compile cython, instead of doing
    a fast install from a wheel.

So, we chose to speep up the common cases, at the cost of requiring an
explicit installation of Cython in the non common cases (1) and (3).
"""


###############################################################################
# Custom distutils commands

DEBUG = False # whether to compile files with -g

def my_cythonize(extensions):
    try:
        import Cython
        if Cython.__version__ < '0.25':
            print ('WARNING: required cython>0.25, found %s. The .c files will '
                   'NOT be regenerated' % Cython.__version__)
            raise ImportError
        from Cython.Build import cythonize
    except ImportError:
        return cythonize_dummy(extensions)
    else:
        return cythonize(extensions, gdb_debug=DEBUG)

def cythonize_dummy(extensions):
    def cname(fname):
        return fname.replace('.pyx', '.c').replace('.py', '.c')
    #
    for ext in extensions:
        ext.sources = [cname(s) for s in ext.sources]
        for src in ext.sources:
            if not os.path.exists(src):
                print ('%s does not exist and Cython is not installed. '
                       'Please install Cython to regenerate it '
                       'automatically.' % src)
                sys.exit(1)
    return extensions


class my_sdist(sdist):
    """
    Same as the standard sdist, but make sure to cythonize the files first.
    """

    def run(self):
        my_cythonize(self.distribution.ext_modules)
        return sdist.run(self)


class my_build_ext(build_ext):
    """
    Same as the standard build_ext, but tries to handle cythonize as much
    transparently as possible. In particular, if Cython is not installed, it
    tries to reuse the existing *.c files which were included in the sdist.
    """
    def build_extensions(self):
        self.extensions = my_cythonize(self.extensions)
        return build_ext.build_extensions(self)

# end of the custom commands section
###############################################################################


def get_cython_extensions():
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
    return [getext(f) for f in files]


if hasattr(sys, 'pypy_version_info'):
    # on PyPy
    USE_CYTHON = False
else:
    # on CPython
    USE_CYTHON = os.environ.get('USE_CYTHON', '1')
    USE_CYTHON = int(USE_CYTHON)

if USE_CYTHON:
    ext_modules = get_cython_extensions()
    extra_install_requires = ['cython>=0.25']
else:
    ext_modules = []
    extra_install_requires = []


setup(name="capnpy",
      author='Antonio Cuni',
      author_email='anto.cuni@gmail.com',
      url='https://github.com/antocuni/capnpy',
      use_scm_version=True,
      include_package_data=True,
      cmdclass={
          'sdist': my_sdist,
          'build_ext': my_build_ext,
      },
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
