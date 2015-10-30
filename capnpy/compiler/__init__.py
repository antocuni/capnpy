import py
import sys
import types
from collections import defaultdict
import subprocess
from pypytools.codegen import Code
from capnpy.type import Types
from capnpy.convert_case import from_camel_case
from capnpy import schema
from capnpy.message import loads

# the following imports have side-effects, and augment the schema.* classes
# with emit() methods
import capnpy.compiler.request
import capnpy.compiler.node
import capnpy.compiler.struct_


## # pycapnp will be supported only until the boostrap is completed
## USE_PYCAPNP = False

## if USE_PYCAPNP:
##     import capnp
##     import schema_capnp
##     def loads(buf, payload_type):
##         return payload_type.from_bytes(buf)
## else:


class ModuleGenerator(object):

    def __init__(self, request, convert_case=True, pyx=False):
        self.code = Code()
        self.request = request
        self.convert_case = convert_case
        self.pyx = pyx
        self.allnodes = {} # id -> node
        self.children = defaultdict(list) # nodeId -> nested nodes
 
    def w(self, *args, **kwargs):
        self.code.w(*args, **kwargs)

    def block(self, *args, **kwargs):
        return self.code.block(*args, **kwargs)

    def _shortname(self, node):
        return node.displayName[node.displayNamePrefixLength:]

    def _pyname_for_file(self, fname):
        return '_%s' % py.path.local(fname).purebasename

    def _pyname(self, node):
        if node.scopeId == 0:
            return self._shortname(node)
        parent = self.allnodes[node.scopeId]
        if parent.which() == schema.Node.__tag__.file:
            if self.current_scope.id == parent.id:
                # no need for fully qualified names for children of the current file
                return self._shortname(node)
            else:
                return '%s.%s' % (self._pyname_for_file(parent.displayName),
                                  self._shortname(node))
        else:
            return '%s.%s' % (self._pyname(parent), self._shortname(node))

    def generate(self):
        self.request.emit(self)
        return self.code.build()

    def _dump_node(self, node):
        def visit(node, deep=0):
            print '%s%s: %s' % (' ' * deep, node.which(), self._shortname(node))
            for child in self.children[node.id]:
                visit(child, deep+2)
        visit(node)


    def visit_const(self, node):
        # XXX: this works only for numerical consts so far
        name = self._shortname(node)
        val = self._get_value(node.const.value)
        self.w("%s = %s" % (name, val))

    def _get_value(self, value):
        val_type = str(value.which())
        return getattr(value, val_type)

    def _convert_name(self, name):
        if self.convert_case:
            return from_camel_case(name)
        else:
            return name

    def _field_name(self, field):
        return self._convert_name(field.name)

    def visit_field(self, field, data_size, ptrs_size):
        fname = self._field_name(field)
        which = field.which()
        if which == schema.Field.__tag__.group:
            self.visit_field_group(fname, field, data_size, ptrs_size)
        elif which == schema.Field.__tag__.slot:
            self.visit_field_slot(fname, field, data_size, ptrs_size)
        else:
            assert False, 'Unkown field kind: %s' % field.which()
        #
        if field.discriminantValue != schema.Field.noDiscriminant:
            line = '{name} = __.field.Union({discriminantValue}, {name})'
            line = line.format(name=fname, discriminantValue=field.discriminantValue)
            self.w(line)

    def visit_field_slot(self, fname, field, data_size, ptrs_size, nullable_by=None):
        kwds = {}
        t = field.slot.type
        which = str(t.which()) # XXX
        if t.is_primitive():
            t = getattr(Types, which)
            size = t.calcsize()
            delta = 0
            kwds['typename'] = t.name
            kwds['default'] = self._get_value(field.slot.defaultValue)
            if nullable_by:
                kwds['nullable_by'] = nullable_by
                decl = ('__.field.NullablePrimitive("{name}", {offset}, '
                        '__.Types.{typename}, default_={default}, '
                        'nullable_by={nullable_by})')
            else:
                decl = ('__.field.Primitive("{name}", {offset}, '
                        '__.Types.{typename}, default_={default})')
        #
        elif which == 'bool':
            size = 0
            delta = 0
            byteoffset, bitoffset = divmod(field.slot.offset, 8)
            kwds['byteoffset'] = byteoffset
            kwds['bitoffset'] = bitoffset
            kwds['default'] = self._get_value(field.slot.defaultValue)
            decl = '__.field.Bool("{name}", {byteoffset}, {bitoffset}, default={default})'
        elif which == 'text':
            decl = '__.field.String("{name}", {offset})'
        elif which == 'data':
            decl = '__.field.Data("{name}", {offset})'
        elif which == 'struct':
            kwds['structname'] = self._get_typename(field.slot.type)
            decl = '__.field.Struct("{name}", {offset}, {structname})'
        elif which == 'list':
            kwds['itemtype'] = self._get_typename(field.slot.type.list.elementType)
            decl = '__.field.List("{name}", {offset}, {itemtype})'
        elif which == 'enum':
            kwds['enumname'] = self._get_typename(field.slot.type)
            decl = '__.field.Enum("{name}", {offset}, {enumname})'
        elif which == 'void':
            decl = '__.field.Void("{name}")'
        elif which == 'anyPointer':
            decl = '__.field.AnyPointer("{name}", {offset})'
        else:
            raise ValueError('Unknown type: %s' % field.slot.type)
        #
        if field.slot.hadExplicitDefault and 'default' not in kwds:
            raise ValueError("explicit defaults not supported for field %s" % field)
        #
        if not field.slot.type.is_bool():
            kwds['offset'] = field.slot.get_offset(data_size)
        kwds['name'] = fname
        line = '{name} = ' + decl
        self.w(line.format(**kwds))

    def visit_field_group(self, fname, field, data_size, ptrs_size):
        ngroup = field.is_nullable(self)
        if ngroup:
            self.visit_nullable_group(ngroup, data_size, ptrs_size)
        else:
            group = self.allnodes[field.group.typeId]
            group.emit_definition(self)
            #self.visit_struct(group)
            self.w('%s = __.field.Group(%s)' % (fname, self._pyname(group)))

    def visit_nullable_group(self, ngroup, data_size, ptrs_size):
        self.visit_field_slot(ngroup.is_null_name, ngroup.is_null, data_size, ptrs_size)
        self.visit_field_slot(ngroup.name, ngroup.value, data_size, ptrs_size,
                              nullable_by=ngroup.is_null_name)

    def visit_enum(self, node):
        name = self._shortname(node)
        items = [self._field_name(item) for item in node.enum.enumerants]
        self._emit_enum(name, name, items)

    def _emit_enum(self, var_name, enum_name, items):
        items = map(repr, items)
        decl = "%s = __.enum(%r, (%s))" % (var_name, enum_name, ', '.join(items))
        self.w(decl)

    def _get_typename(self, t):
        which = str(t.which()) # XXX
        if t.is_builtin():
            return '__.Types.%s' % which
        elif which == 'struct':
            return self._pyname(self.allnodes[t.struct.typeId])
        elif which == 'enum':
            return self._pyname(self.allnodes[t.enum.typeId])
        else:
            assert False



class Compiler(object):

    def __init__(self, path, convert_case=True, pyx=False):
        self.path = [py.path.local(dirname) for dirname in path]
        self.convert_case = convert_case
        self.modules = {}
        self.pyx = pyx
        if self.pyx:
            self.tmpdir = py.path.local.mkdtemp()
        else:
            self.tmpdir = None

    def load_schema(self, filename):
        filename = self._find_file(filename)
        try:
            return self.modules[filename]
        except KeyError:
            mod = self.compile_file(filename)
            self.modules[filename] = mod
            return mod

    def generate_py_source(self, data):
        request = loads(data, schema.CodeGeneratorRequest)
        m = ModuleGenerator(request, self.convert_case, self.pyx)
        src = m.generate()
        return m, py.code.Source(src)

    def compile_file(self, filename):
        data = self._capnp_compile(filename)
        m, src = self.generate_py_source(data)
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
        mod.__source__ = str(src)
        mod.__dict__['__compiler'] = self
        exec src.compile() in mod.__dict__
        return mod

    def _compile_pyx(self, filename, m, src):
        """
        Use Cython to compile the schema
        """
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
        sys.modules[m.tmpname] = tmpmod
        mod = imp.load_dynamic(m.modname, str(dll))
        #
        # clean-up the cluttered sys.modules
        del sys.modules[mod.__name__]
        del sys.modules[tmpmod.__name__]
        return mod

    def _find_file(self, filename):
        if not filename.startswith('/'):
            raise ValueError("schema paths must be absolute: %s" % filename)
        for dirpath in self.path:
            f = dirpath.join(filename)
            if f.check(file=True):
                return f
        raise ValueError("Cannot find %s in the given path" % filename)

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

_compiler = Compiler(sys.path)
load_schema = _compiler.load_schema
