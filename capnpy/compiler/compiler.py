import py
import sys
import types
import subprocess
from capnpy import schema
from capnpy.message import loads
from capnpy.blob import PYX
from capnpy.compiler.module import ModuleGenerator


class BaseCompiler(object):

    standalone = None

    def __init__(self, path, pyx):
        self.path = [py.path.local(dirname) for dirname in path]
        self.modules = {}
        #
        assert pyx in (True, False, 'auto')
        if pyx == 'auto':
            pyx = PYX
        self.pyx = pyx
        if self.pyx:
            assert PYX, 'Cython extensions are missing; please run setup.py install'
            self.tmpdir = py.path.local.make_numbered_dir('capnpy-pyx-')
        else:
            self.tmpdir = None

    def generate_py_source(self, filename, convert_case):
        data = self._capnp_compile(filename)
        request = loads(data, schema.CodeGeneratorRequest)
        m = ModuleGenerator(request, convert_case, self.pyx, self.standalone)
        src = m.generate()
        return m, py.code.Source(src)

    def _capnp_compile(self, filename):
        # this is a hack: we use cat as a plugin of capnp compile to get the
        # CodeGeneratorRequest bytes. There MUST be a more proper way to do that
        cmd = ['capnp', 'compile', '-o', '/bin/cat']
        for dirname in self.path:
            cmd.append('-I%s' % dirname)
        cmd.append(str(filename))
        #print ' '.join(cmd)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        ret = proc.wait()
        if ret != 0:
            raise ValueError(stderr)
        return stdout


class DynamicCompiler(BaseCompiler):
    """
    A compiler to compile and load schemas on the fly
    """

    standalone = False

    def load_schema(self, modname=None, importname=None, filename=None, convert_case=True):
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
        """
        filename = self._get_filename(modname, importname, filename)
        try:
            return self.modules[filename]
        except KeyError:
            mod = self._compile_file(filename, convert_case)
            self.modules[filename] = mod
            return mod

    def _compile_file(self, filename, convert_case):
        m, src = self.generate_py_source(filename, convert_case)
        if self.pyx:
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
        from pyximport.pyxbuild import pyx_to_dll
        pyxname = filename.new(ext='pyx')
        pyxfile = self.tmpdir.join(pyxname).ensure(file=True)
        pyxfile.write(src)
        dll = pyx_to_dll(str(pyxfile), pyxbuild_dir=str(self.tmpdir))
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

    standalone = True

    def compile(self, filename, convert_case=True):
        infile = py.path.local(filename)
        outfile = infile.new(ext='.py') # or .pyx?
        m, src = self.generate_py_source(infile, convert_case=convert_case)
        outfile.write(src)
