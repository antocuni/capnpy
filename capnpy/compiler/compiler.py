from __future__ import absolute_import
import py
import sys
import os
import types
import subprocess
from distutils.version import LooseVersion
import capnpy
from capnpy import schema
from capnpy.message import loads
from capnpy.blob import PYX
from capnpy.compiler.module import ModuleGenerator

PKGDIR = py.path.local(capnpy.__file__).dirpath()

class CompilerError(Exception):
    pass

class BaseCompiler(object):

    standalone = None
    annotate = False
    include_dirs = [str(PKGDIR)] # include "ptr.h"

    def __init__(self, path):
        self.path = [py.path.local(dirname) for dirname in path]
        self.modules = {}
        self._tmpdir = None

    @property
    def tmpdir(self):
        if self._tmpdir is None:
            self._tmpdir = py.path.local.make_numbered_dir('capnpy-pyx-')
        return self._tmpdir

    def getpyx(self, pyx):
        assert pyx in (True, False, 'auto')
        if pyx == 'auto':
            pyx = PYX
        if pyx and not PYX:
            raise ValueError('Cython extensions are missing; '
                             'please run setup.py install')
        return pyx

    def _parse_schema_file(self, filename):
        data = self._capnp_compile(filename)
        request = loads(data, schema.CodeGeneratorRequest)
        return request

    def generate_py_source(self, filename, convert_case, pyx):
        pyx = self.getpyx(pyx)
        request = self._parse_schema_file(filename)
        m = ModuleGenerator(request, convert_case, pyx, self.standalone)
        src = m.generate()
        return m, py.code.Source(src)

    def _pyx_to_dll(self, filename, m, src):
        from pyximport.pyxbuild import pyx_to_dll
        pyxname = filename.new(ext='pyx')
        pyxfile = self.tmpdir.join(pyxname).ensure(file=True)
        pyxfile.write(src)
        if self.annotate:
            import Cython.Compiler.Options
            Cython.Compiler.Options.annotate = True
        dll = pyx_to_dll(str(pyxfile),
                         pyxbuild_dir=str(self.tmpdir),
                         setup_args=dict(
                             include_dirs=self.include_dirs,
                         ))
        if self.annotate and pyxfile.basename != 'annotate.pyx':
            htmlfile = pyxfile.new(ext='html')
            os.system('xdg-open %s' % htmlfile)
        return dll

    def _capnp_compile(self, filename):
        # this is a hack: we use cat as a plugin of capnp compile to get the
        # CodeGeneratorRequest bytes. There MUST be a more proper way to do that
        capnp = py.path.local.sysfind('capnp')
        if capnp is None:
            raise CompilerError("Cannot find the capnp executable. Make sure it is "
                                "installed and in $PATH")
        #
        self._capnp_check_version()
        cmd = ['capnp', 'compile', '-o', '/bin/cat']
        for dirname in self.path:
            cmd.append('-I%s' % dirname)
        cmd.append(str(filename))
        return self._exec(*cmd)

    def _capnp_check_version(self):
        version = self._exec('capnp', '--version')
        version = version.strip()
        if not version.startswith("Cap'n Proto version"):
            raise CompilerError("capnp version string not recognized: %s" % version)
        _, version = version.rsplit(' ', 1)
        if version < LooseVersion('0.5.0'):
            raise CompilerError("The capnp executable is too old: the minimum required "
                                "version is 0.5.0")

    def _exec(self, *cmd):
        #print ' '.join(cmd)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        ret = proc.wait()
        if ret != 0:
            raise CompilerError(stderr)
        return stdout


class DynamicCompiler(BaseCompiler):
    """
    A compiler to compile and load schemas on the fly
    """

    standalone = False

    def parse_schema(self, modname=None, importname=None, filename=None):
        filename = self._get_filename(modname, importname, filename)
        return self._parse_schema_file(filename)

    def load_schema(self, modname=None, importname=None, filename=None,
                    convert_case=True, pyx='auto'):
        """
        Compile and load a capnp schema, which can be specified by setting one
        (and only one) of the following params:

          - *modname*: in the form 'a.b.c', it will search the file
             a/b/c.capnp in the directories of the path. This is useful if you
             want to distribute the schema file together with your python
             package

          - *importname*: similar to *modname*, but using the same syntax as
             the ``import`` expression in capnp schemas; in the example above,
             it becomes "/a/b/c.capnp". The starting slash indicates that it
             is an non-relative import, i.e. that it will be looked in all the
             directories listed in path

          - *filename*: the (relative or absolute) file containing the schema;
             no search if performed

        You can specify the following options:

          - *convert_case*: whether to convert camelCase to
            camel_case. Default is True.

          - *pyx*: specify whether to use **pyx mode** or **py mode**.
            Default is 'auto'
        """
        pyx = self.getpyx(pyx)
        filename = self._get_filename(modname, importname, filename)
        try:
            return self.modules[filename]
        except KeyError:
            mod = self._compile_file(filename, convert_case, pyx)
            self.modules[filename] = mod
            return mod

    def _compile_file(self, filename, convert_case, pyx):
        m, src = self.generate_py_source(filename, convert_case=convert_case,
                                         pyx=pyx)
        if pyx:
            return self._compile_pyx(filename, m, src)
        else:
            return self._compile_py(filename, m, src)

    def _compile_py(self, filename, m, src):
        """
        Compile and load the schema as pure python
        """
        mod = types.ModuleType(m.modname)
        mod.__file__ = str(filename)
        mod.__schema__ = str(filename)
        mod.__source__ = str(src)
        mod.__dict__['__compiler'] = self
        exec src.compile() in mod.__dict__
        return mod

    def _compile_pyx(self, filename, m, src):
        """
        Use Cython to compile the schema
        """
        import capnpy.ext # the package which we will load the .so in
        import imp
        #
        # the generated file needs a reference to __compiler to be able to
        # import other schemas. In pure-python mode, we simply inject
        # __compiler in the __dict__ before compiling the source; but in pyx
        # mode we cannot, hence we need a way to "pass" an argument from the
        # outside. I think the only way is to temporarily stick it in some
        # global state, for example sys.modules. Then, as we don't want to
        # clutter any global state, we cleanup sys.modules.
        #
        # So, when compiling foo.capnp, we create a dummy foo_tmp module which
        # contains __compiler. Then, in foo.pyx, we import it:
        #     from foo_tmp import __compiler
        #
        dll = self._pyx_to_dll(filename, m, src)
        tmpmod = types.ModuleType(m.tmpname)
        tmpmod.__dict__['__compiler'] = self
        tmpmod.__dict__['__schema__'] = str(filename)
        sys.modules[m.tmpname] = tmpmod
        modname = 'capnpy.ext.%s' % m.modname
        mod = imp.load_dynamic(modname, str(dll))
        #
        # clean-up the cluttered sys.modules
        del sys.modules[mod.__name__]
        del sys.modules[tmpmod.__name__]
        return mod

    def _get_filename(self, modname, importname, filename):
        n = (modname, importname, filename).count(None)
        if n != 2:
            raise ValueError("You have to specify exactly 1 of modname, importname or filename")
        #
        if modname is not None:
            importname = '%s.capnp' % modname.replace('.', '/')
            return self._find_file(importname)
        elif importname is not None:
            if not importname.startswith('/'):
                raise ValueError("schema paths must be absolute: %s" % importname)
            return self._find_file(importname)
        else:
            return py.path.local(filename)

    def _find_file(self, importname):
        for dirpath in self.path:
            f = dirpath.join(importname)
            if f.check(file=True):
                return f
        raise ValueError("Cannot find %s in the given path" % importname)


class StandaloneCompiler(BaseCompiler):
    """
    Standalone compiler: instead of loading schemas on the fly, it generates
    .py/.so/.dll files to be imported by the standard ``import`` statement
    """

    standalone = True

    def compile(self, filename, convert_case=True, pyx='auto'):
        pyx = self.getpyx(pyx)
        infile = py.path.local(filename)
        m, src = self.generate_py_source(infile, convert_case, pyx)
        if pyx:
            self._compile_pyx(infile, m, src)
        else:
            self._compile_py(infile, m, src)

    def _compile_py(self, infile, m, src):
        outfile = infile.new(ext='.py')
        outfile.write(src)

    def _compile_pyx(self, infile, m, src):
        dll = self._pyx_to_dll(infile, m, src)
        dll = py.path.local(dll)
        outdir = infile.dirpath()
        dll.copy(outdir, mode=True)


class DistutilsCompiler(BaseCompiler):
    """
    Compiler for integration with distutils: it generates .py/.pyx files,
    which (in case of pyx files) are then handled by cythonize
    """
    standalone = True

    def compile(self, filename, convert_case=True, pyx='auto'):
        pyx = self.getpyx(pyx)
        infile = py.path.local(filename)
        if pyx:
            outfile = infile.new(ext='pyx')
        else:
            outfile = infile.new(ext='py')
        #
        if outfile.exists() and outfile.mtime() > infile.mtime():
            # already compiled
            return outfile
        cwd = py.path.local('.')
        print '[capnpy] Compiling', infile.relto(cwd)
        m, src = self.generate_py_source(infile, convert_case=convert_case,
                                         pyx=pyx)
        outfile.write(src)
        return outfile
