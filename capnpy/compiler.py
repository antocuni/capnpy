import py
import sys
import types
from collections import defaultdict
from datetime import datetime
import subprocess
from pypytools.codegen import Code
from capnpy.type import Types
from capnpy.convert_case import from_camel_case

## # pycapnp will be supported only until the boostrap is completed
## USE_PYCAPNP = False

## if USE_PYCAPNP:
##     import capnp
##     import schema_capnp
##     def loads(buf, payload_type):
##         return payload_type.from_bytes(buf)
## else:
from capnpy import schema
from capnpy.message import loads


class FileGenerator(object):

    def __init__(self, request, convert_case=True):
        self.code = Code()
        self.request = request
        self.convert_case = convert_case
        self.allnodes = {} # id -> node
        self.children = defaultdict(list) # nodeId -> nested nodes
        self.allfiles = []
 
    def w(self, *args, **kwargs):
        self.code.w(*args, **kwargs)

    def block(self, *args, **kwargs):
        return self.code.block(*args, **kwargs)

    def _shortname(self, node):
        return node.displayName[node.displayNamePrefixLength:]

    def _pyname_for_file(self, fname):
        return '__%s' % py.path.local(fname).purebasename

    def _pyname(self, node):
        if node.scopeId == 0:
            return self._shortname(node)
        parent = self.allnodes[node.scopeId]
        if parent.which() == schema.Node.__tag__.file:
            if self.current_scope == parent:
                # no need for fully qualified names for children of the current file
                return self._shortname(node)
            else:
                return '%s.%s' % (self._pyname_for_file(parent.displayName),
                                  self._shortname(node))
        else:
            return '%s.%s' % (self._pyname(parent), self._shortname(node))

    def generate(self):
        self.visit_request(self.request)
        return self.code.build()

    def visit_request(self, request):
        for node in request.nodes:
            self.allnodes[node.id] = node
            # roots have scopeId == 0, so children[0] will contain them
            self.children[node.scopeId].append(node)
            if node.which() == schema.Node.__tag__.file:
                self.allfiles.append(node.displayName)
        #
        for f in request.requestedFiles:
            self.visit_file(f)

    def _dump_node(self, node):
        def visit(node, deep=0):
            print '%s%s: %s' % (' ' * deep, node.which(), self._shortname(node))
            for child in self.children[node.id]:
                visit(child, deep+2)
        visit(node)

    def visit_file(self, f):
        node = self.allnodes[f.id]
        self.current_scope = node
        self.w("# THIS FILE HAS BEEN GENERATED AUTOMATICALLY BY capnpy")
        self.w("# do not edit by hand")
        self.w("# generated on %s" % datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.w("# input files: ")
        for f in self.request.requestedFiles:
            self.w("#   - %s" % f.filename)
        self.w("")
        self.w("from capnpy.struct_ import Struct, undefined")
        self.w("from capnpy import field")
        self.w("from capnpy.enum import enum")
        self.w("from capnpy.blob import Types")
        self.w("from capnpy.structor import structor")
        self.w("from capnpy.util import extend")
        self.w("")
        self.declare_imports(f)
        self.w("")
        #
        # first of all, we emit all the non-structs and "predeclare" all the
        # structs
        structs = []
        children = self.children[node.id]
        for child in children:
            which = child.which()
            if which == schema.Node.__tag__.struct:
                self.declare_struct(child)
                structs.append(child)
            elif which == schema.Node.__tag__.enum:
                self.visit_enum(child)
            elif which == schema.Node.__tag__.annotation:
                # annotations are simply ignored for now
                pass
            else:
                assert False, 'Unkown node type: %s' % which
        #
        # then, we emit the body of all the structs we declared earlier
        for child in structs:
            self.visit_struct(child)
        #
        modname = py.path.local(f.filename).purebasename
        self.w("")
        self.w("try:")
        self.w("    import %s_extended # side effects" % modname)
        self.w("except ImportError:")
        self.w("    pass")

    def declare_imports(self, f):
        for fname in self.allfiles:
            if fname != f.filename:
                self.w('{decl_name} = __compiler.load_schema("{fname}")',
                       decl_name = self._pyname_for_file(fname),
                       fname = fname)

    def declare_struct(self, node):
        name = self._shortname(node)
        with self.block("class %s(Struct):" % name):
            for child in self.children[node.id]:
                if child.which() == schema.Node.__tag__.struct:
                    self.declare_struct(child)
            self.w("pass")

    def visit_struct(self, node):
        name = self._pyname(node)
        self.w("")
        self.w("@extend(%s)" % name)
        with self.block("class _:"):
            data_size = node.struct.dataWordCount
            ptrs_size = node.struct.pointerCount
            self.w("__data_size__ = %d" % data_size)
            self.w("__ptrs_size__ = %d" % ptrs_size)
            for child in self.children[node.id]:
                which = child.which()
                if which == schema.Node.__tag__.const:
                    self.visit_const(child)
                elif which == schema.Node.__tag__.struct:
                    if not child.struct.isGroup:
                        self.visit_struct(child)
                else:
                    assert False
            if node.struct.discriminantCount:
                self._emit_tag(node)
            if node.struct.fields is not None:
                for field in node.struct.fields:
                    self.visit_field(field, data_size, ptrs_size)
                self._emit_struct_ctors(node)

    def _emit_tag(self, node):
        # union tags are 16 bits, so *2
        tag_offset = node.struct.discriminantOffset * 2
        enum_items = [None] * node.struct.discriminantCount
        for field in node.struct.fields:
            i = field.discriminantValue
            if i != schema.Field.noDiscriminant:
                enum_items[i] = self._field_name(field)
        enum_name = '%s.__tag__' % self._shortname(node)
        self.w("__tag_offset__ = %s" % tag_offset)
        self._emit_enum('__tag__', enum_name, enum_items)

    def _emit_struct_ctors(self, node):
        if node.struct.discriminantCount:
            self._emit_ctors_union(node)
        else:
            self._emit_ctor_nounion(node)

    def _emit_ctor_nounion(self, node):
        fnames = [self._field_name(f) for f in node.struct.fields]
        flist = "[%s]" % ', '.join(fnames)
        # normally, __new__ is special-cased at class creation time and
        # automatically turned into a staticmethod; however, here we are
        # inside an @extend body, so we need to call it manually
        self.w("__new__ = structor('__new__', __data_size__, __ptrs_size__, {flist})",
               flist=flist)
        self.w("__new__ = staticmethod(__new__)")

    def _emit_ctors_union(self, node):
        # suppose we have a tag whose members are 'circle' and 'square': we
        # create three ctors:
        #
        #     def __new__(cls, x, y, square=undefined, circle=undefined):  ...
        #
        #     @classmethod
        #     def new_square(cls, x, y): ...
        #
        #     @classmethod
        #     def new_circle(cls, x, y): ...
        #
        # when calling __new__, one and only one of square and circle must be given. 
        #
        std_fields = [] # non-union fields
        tag_fields = [] # union fields
        for f in node.struct.fields:
            if f.discriminantValue == schema.Field.noDiscriminant:
                std_fields.append(f)
            else:
                tag_fields.append(f)
        #
        # now, we create a separate ctor for each tag value
        for tag_field in tag_fields:
            fnames = ['%s.field' % self._field_name(tag_field)]
            fnames += [self._field_name(f) for f in std_fields]
            flist = "[%s]" % ', '.join(fnames)
            self.w("new_{name} = classmethod(structor('new_{name}', __data_size__, "
                   "__ptrs_size__, {flist}, __tag_offset__, __tag__.{name}))",
                   name=self._field_name(tag_field), flist=flist)
        #
        # finally, create the __new__
        # def __new__(cls, x, y, square=undefined, circle=undefined):
        #     if square is not undefined:
        #         self._assert_undefined(circle, 'circle', 'square')
        #         return cls.new_square(x=x, y=y)
        #     if circle is not undefined:
        #         self._assert_undefined(square, 'square', 'circle')
        #         return cls.new_circle(x=x, y=y)
        #     raise TypeError("one of the following args is required: square, circle")
        args = [self._field_name(f) for f in std_fields]
        for f in tag_fields:
            args.append('%s=undefined' % self._field_name(f))
        self.w('@staticmethod')
        with self.block('def __new__(cls, {arglist}):', arglist=self.code.args(args)):
            for tag_field in tag_fields:
                tag_field_name = self._field_name(tag_field)
                with self.block('if {name} is not undefined:', name=tag_field_name):
                    # emit the series of _assert_undefined, for each other tag field
                    for other_tag_field in tag_fields:
                        if other_tag_field is tag_field:
                            continue
                        self.w('cls._assert_undefined({fname}, "{fname}", "{myname}")',
                               fname=self._field_name(other_tag_field),
                               myname=tag_field_name)
                    #
                    # return cls.new_square(x=x, y=y)
                    args = [self._field_name(f) for f in std_fields]
                    args.append(self._field_name(tag_field))
                    args = ['%s=%s' % (arg, arg) for arg in args]
                    self.w('return cls.new_{ctor}({args})',
                           ctor=tag_field_name, args=self.code.args(args))
            #
            tags = [self._field_name(f) for f in tag_fields]
            tags = ', '.join(tags)
            self.w('raise TypeError("one of the following args is required: {tags}")',
                   tags=tags)

    def visit_const(self, node):
        # XXX: this works only for numerical consts so far
        name = self._shortname(node)
        val = self._get_value(node.const.value)
        self.w("%s = %s" % (name, val))

    def _get_value(self, value):
        val_type = str(value.which())
        return getattr(value, val_type)

    def _field_name(self, field):
        if self.convert_case:
            return from_camel_case(field.name)
        else:
            return field.name

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
            line = '{name} = field.Union({discriminantValue}, {name})'
            line = line.format(name=fname, discriminantValue=field.discriminantValue)
            self.w(line)

    def visit_field_slot(self, fname, field, data_size, ptrs_size):
        kwds = {}
        t = field.slot.type
        which = str(t.which()) # XXX
        if t.is_primitive():
            t = getattr(Types, which)
            size = t.calcsize()
            delta = 0
            kwds['typename'] = t.name
            kwds['default'] = self._get_value(field.slot.defaultValue)
            decl = ('field.Primitive("{name}", {offset}, '
                    'Types.{typename}, default={default})')
        #
        elif which == 'bool':
            size = 0
            delta = 0
            byteoffset, bitoffset = divmod(field.slot.offset, 8)
            kwds['byteoffset'] = byteoffset
            kwds['bitoffset'] = bitoffset
            kwds['default'] = self._get_value(field.slot.defaultValue)
            decl = 'field.Bool("{name}", {byteoffset}, {bitoffset}, default={default})'
        elif which == 'text':
            size = 8
            delta = data_size*8 # it's a pointer
            decl = 'field.String("{name}", {offset})'
        #
        elif which == 'data':
            size = 8
            delta = data_size*8 # it's a pointer
            decl = 'field.Data("{name}", {offset})'
        #
        elif which == 'struct':
            size = 8
            delta = data_size*8 # it's a pointer
            kwds['structname'] = self._get_typename(field.slot.type)
            decl = 'field.Struct("{name}", {offset}, {structname})'
        #
        elif which == 'list':
            size = 8
            delta = data_size*8 # it's a pointer
            kwds['itemtype'] = self._get_typename(field.slot.type.list.elementType)
            decl = 'field.List("{name}", {offset}, {itemtype})'
        #
        elif which == 'enum':
            size = 2
            delta = 0
            kwds['enumname'] = self._get_typename(field.slot.type)
            decl = 'field.Enum("{name}", {offset}, {enumname})'
        #
        elif which == 'void':
            size = 0
            delta = 0
            decl = 'field.Void("{name}")'
        #
        elif which == 'anyPointer':
            size = 8
            delta = data_size*8
            decl = 'field.AnyPointer("{name}", {offset})'
        else:
            raise ValueError('Unknown type: %s' % field.slot.type)
        #
        if field.slot.hadExplicitDefault and 'default' not in kwds:
            raise ValueError("explicit defaults not supported for field %s" % field)
        kwds['offset'] = delta + field.slot.offset*size
        kwds['name'] = fname
        line = '{name} = ' + decl
        self.w(line.format(**kwds))

    def visit_field_group(self, fname, field, data_size, ptrs_size):
        group = self.allnodes[field.group.typeId]
        self.visit_struct(group)
        self.w('%s = field.Group(%s)' % (fname, self._pyname(group)))

    def visit_enum(self, node):
        name = self._shortname(node)
        items = [self._field_name(item) for item in node.enum.enumerants]
        self._emit_enum(name, name, items)

    def _emit_enum(self, var_name, enum_name, items):
        items = map(repr, items)
        decl = "%s = enum(%r, (%s))" % (var_name, enum_name, ', '.join(items))
        self.w(decl)

    def _get_typename(self, t):
        which = str(t.which()) # XXX
        if t.is_builtin():
            return 'Types.%s' % which
        elif which == 'struct':
            return self._pyname(self.allnodes[t.struct.typeId])
        elif which == 'enum':
            return self._pyname(self.allnodes[t.enum.typeId])
        else:
            assert False


class Compiler(object):

    def __init__(self, path, convert_case=True):
        self.path = [py.path.local(dirname) for dirname in path]
        self.convert_case = convert_case
        self.modules = {}

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
        gen = FileGenerator(request, self.convert_case)
        src = gen.generate()
        return request, py.code.Source(src)

    def compile_file(self, filename):
        data = self._capnp_compile(filename)
        request, src = self.generate_py_source(data)
        mod = types.ModuleType(filename.purebasename)
        mod.__file__ = str(filename)
        mod.__source__ = str(src)
        mod.__dict__['__compiler'] = self
        exec src.compile() in mod.__dict__
        return mod

    def _find_file(self, filename):
        if filename.startswith('/'):
            return py.path.local(filename)
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
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        ret = proc.wait()
        if ret != 0:
            raise ValueError(stderr)
        return stdout

_compiler = Compiler(sys.path)
load_schema = _compiler.load_schema

def main():
    #data = sys.stdin.read()
    data = _capnp_compile(sys.argv[1])
    request, src = generate_py_source(data)
    print src

if __name__ == '__main__':
    main()
