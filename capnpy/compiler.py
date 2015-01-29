import py
import sys
import types
from collections import defaultdict
from datetime import datetime
import subprocess
from pypytools.codegen import Code
from capnpy.type import Types

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

    def __init__(self, request):
        self.code = Code()
        self.request = request
        self.allnodes = {} # id -> node
        self.children = defaultdict(list) # nodeId -> nested nodes
 
    def w(self, *args, **kwargs):
        self.code.w(*args, **kwargs)

    def block(self, *args, **kwargs):
        return self.code.block(*args, **kwargs)

    def _shortname(self, node):
        return node.displayName[node.displayNamePrefixLength:]

    def _pyname(self, node):
        if node.scopeId == 0:
            return self._shortname(node)
        parent = self.allnodes[node.scopeId]
        if parent.which() == schema.Node.__tag__.file:
            # we don't need to use fully qualified names for children of files
            return self._shortname(node)
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
        #
        for f in request.requestedFiles:
            self.visit_file(f)

    def _dump_node(self, node):
        def visit(node, deep=0):
            print '%s%s: %s' % (' ' * deep, mywhich(node), self._shortname(node))
            for child in self.children[node.id]:
                visit(child, deep+2)
        visit(node)

    def visit_file(self, f):
        node = self.allnodes[f.id]
        self.w("# THIS FILE HAS BEEN GENERATED AUTOMATICALLY BY capnpy")
        self.w("# do not edit by hand")
        self.w("# generated on %s" % datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.w("# input files: ")
        for f in self.request.requestedFiles:
            self.w("#   - %s" % f.filename)
        self.w("")
        self.w("from capnpy.struct_ import Struct")
        self.w("from capnpy import field")
        self.w("from capnpy.enum import enum")
        self.w("from capnpy.blob import Types")
        self.w("from capnpy.structor import structor")
        self.w("from capnpy.util import extend")
        self.w("undefined = object()")
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
                enum_items[i] = field.name
        enum_name = '%s.__tag__' % self._shortname(node)
        self.w("__tag_offset__ = %s" % tag_offset)
        self._emit_enum('__tag__', enum_name, enum_items)

    def _emit_struct_ctors(self, node):
        if node.struct.discriminantCount:
            self._emit_ctors_union(node)
        else:
            self._emit_ctor_nounion(node)

    def _emit_ctor_nounion(self, node):
        fnames = [f.name for f in node.struct.fields]
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
            fnames = ['%s.field' % tag_field.name]
            fnames += [f.name for f in std_fields]
            flist = "[%s]" % ', '.join(fnames)
            self.w("new_{name} = classmethod(structor('new_{name}', __data_size__, "
                   "__ptrs_size__, {flist}, __tag_offset__, __tag__.{name}))",
                   name=tag_field.name, flist=flist)
        #
        # finally, create the __new__
        args = [f.name for f in std_fields]
        for f in tag_fields:
            args.append('%s=undefined' % f.name)
        self.w('@staticmethod')
        with self.block('def __new__(cls, {arglist}):', arglist=self.code.args(args)):
            for tag_field in tag_fields:
                with self.block('if {name} is not undefined:', name=tag_field.name):
                    args = [f.name for f in std_fields]
                    args.append(tag_field.name)
                    args = ['%s=%s' % (arg, arg) for arg in args]
                    self.w('return cls.new_{ctor}({args})',
                           ctor=tag_field.name, args=self.code.args(args))

    def visit_const(self, node):
        # XXX: this works only for numerical consts so far
        name = self._shortname(node)
        val = self._get_value(node.const.value)
        self.w("%s = %s" % (name, val))

    def _get_value(self, value):
        val_type = str(value.which())
        return getattr(value, val_type)

    def visit_field(self, field, data_size, ptrs_size):
        which = field.which()
        if which == schema.Field.__tag__.group:
            self.visit_field_group(field, data_size, ptrs_size)
        elif which == schema.Field.__tag__.slot:
            self.visit_field_slot(field, data_size, ptrs_size)
        else:
            assert False, 'Unkown field kind: %s' % field.which()
        #
        if field.discriminantValue != schema.Field.noDiscriminant:
            line = '{name} = field.Union({discriminantValue}, {name})'
            line = line.format(name=field.name, discriminantValue=field.discriminantValue)
            self.w(line)

    def visit_field_slot(self, field, data_size, ptrs_size):
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
        kwds['name'] = field.name
        line = '{name} = ' + decl
        self.w(line.format(**kwds))

    def visit_field_group(self, field, data_size, ptrs_size):
        group = self.allnodes[field.group.typeId]
        self.visit_struct(group)
        self.w('%s = field.Group(%s)' % (field.name, self._pyname(group)))

    def visit_enum(self, node):
        name = self._shortname(node)
        items = [item.name for item in node.enum.enumerants]
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

def generate_py_source(data):
    request = loads(data, schema.CodeGeneratorRequest)
    gen = FileGenerator(request)
    src = gen.generate()
    return request, py.code.Source(src)

def compile_file(filename):
    data = _capnp_compile(filename)
    request, src = generate_py_source(data)
    mod = types.ModuleType(filename.purebasename)
    mod.__file__ = str(filename)
    mod.__source__ = str(src)
    exec src.compile() in mod.__dict__
    return mod

def _capnp_compile(filename):
    # this is a hack: we use cat as a plugin of capnp compile to get the
    # CodeGeneratorRequest bytes. There MUST be a more proper way to do that
    proc = subprocess.Popen(['capnp', 'compile', '-o', '/bin/cat', str(filename)],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    ret = proc.wait()
    if ret != 0:
        raise ValueError(stderr)
    return stdout

def main():
    #data = sys.stdin.read()
    data = _capnp_compile(sys.argv[1])
    request, src = generate_py_source(data)
    print src

if __name__ == '__main__':
    main()
