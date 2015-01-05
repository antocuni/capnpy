import py
import sys
import types
from collections import defaultdict
from datetime import datetime
import subprocess
from contextlib import contextmanager
from capnpy.type import Types

# XXX: this is temporarily using pycapnp to bootstrap: we will kill the
# dependency as soon as we can generate our own schema_capnp.py
import capnp
import schema_capnp

## from capnpy import schema as schema_capnp

class CodeBuilder(object):

    def __init__(self):
        self.lines = []
        self.indentation = 0

    def build(self):
        return '\n'.join(self.lines)

    def writeline(self, s):
        self.lines.append(' ' * self.indentation + s)

    @contextmanager
    def indent(self, s=None):
        if s is not None:
            self.writeline(s)
        self.indentation += 4
        yield
        self.indentation -= 4


class FileGenerator(object):

    def __init__(self, request):
        self.builder = CodeBuilder()
        self.request = request
        self.allnodes = {} # id -> node
        self.children = defaultdict(set) # nodeId -> nested nodes
 
    def w(self, s):
        self.builder.writeline(s)

    def block(self, s):
        return self.builder.indent(s)

    def _shortname(self, node):
        return node.displayName[node.displayNamePrefixLength:]

    def _pyname(self, node):
        if node.scopeId == 0:
            return self._shortname(node)
        parent = self.allnodes[node.scopeId]
        if parent.which() == 'file':
            # we don't need to use fully qualified names for children of files
            return self._shortname(node)
        else:
            return '%s.%s' % (self._pyname(parent), self._shortname(node))

    def generate(self):
        self.visit_request(self.request)
        return self.builder.build()

    def visit_request(self, request):
        roots = []
        for node in request.nodes:
            self.allnodes[node.id] = node
            if node.scopeId == 0:
                roots.append(node)
            else:
                self.children[node.scopeId].add(node)
        #
        for root in roots:
            assert root.which() == 'file'
            if root.displayName == 'capnp/c++.capnp':
                continue # ignore this for now
            self.visit_file(root)

    def _dump_node(self, node):
        def visit(node, deep=0):
            print '%s%s: %s' % (' ' * deep, node.which(), self._shortname(node))
            for child in self.scopes[node.id]:
                visit(child, deep+2)
        visit(node)

    def visit_file(self, node):
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
        self.w("from capnpy.util import extend")
        self.w("")
        #
        # first of all, we emit all the non-structs and "predeclare" all the
        # structs
        structs = []
        children = self.children[node.id]
        for child in children:
            which = child.which()
            if which == 'struct':
                self.declare_struct(child)
                structs.append(child)
            elif which == 'enum':
                self.visit_enum(child)
            elif which == 'annotation':
                # annotations are simply ignored for now
                pass
            else:
                assert False, 'Unkown node type: %s' % which
        #
        # then, we emit the body of all the structs we declared earlier
        for child in structs:
            self.visit_struct(child)

    def declare_struct(self, node):
        name = self._shortname(node)
        with self.block("class %s(Struct):" % name):
            for child in self.children[node.id]:
                if child.which() == 'struct':
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
                if which == 'const':
                    self.visit_const(child)
                elif which == 'struct':
                    if not child.struct.isGroup:
                        self.visit_struct(child)
                else:
                    assert False
            if node.struct.discriminantCount:
                self._emit_union_tag(node)
            for field in node.struct.fields:
                self.visit_field(field, data_size, ptrs_size)

    def _emit_union_tag(self, node):
        # union tags are 16 bits, so *2
        union_tag_offset = node.struct.discriminantOffset * 2
        enum_items = [None] * node.struct.discriminantCount
        for field in node.struct.fields:
            i = field.discriminantValue
            if i != schema_capnp.Field.noDiscriminant:
                enum_items[i] = field.name
        enum_name = '%s.__tag__' % self._shortname(node)
        #
        self.w("__tag_offset__ = %s" % union_tag_offset)
        self._emit_enum('__tag__', enum_name, enum_items)

    def visit_const(self, node):
        # XXX: this works only for numerical consts so far
        name = self._shortname(node)
        val = self._get_value(node.const.value)
        self.w("%s = %s" % (name, val))

    def _get_value(self, value):
        val_type = value.which()
        return getattr(value, val_type)

    def visit_field(self, field, data_size, ptrs_size):
        if field.which() == 'group':
            self.visit_field_group(field, data_size, ptrs_size)
        elif field.which() == 'slot':
            self.visit_field_slot(field, data_size, ptrs_size)
        else:
            assert False, 'Unkown field kind: %s' % field.which()
        #
        if field.discriminantValue != schema_capnp.Field.noDiscriminant:
            line = '{name} = field.Union({discriminantValue}, {name})'
            line = line.format(name=field.name, discriminantValue=field.discriminantValue)
            self.w(line)

    def visit_field_slot(self, field, data_size, ptrs_size):
        if field.slot.hadExplicitDefault:
            print 'WARNING: ignoring explicit default for field %s' % field.name
        kwds = {}
        which = field.slot.type.which()
        if Types.is_primitive(which):
            t = getattr(Types, which)
            size = t.calcsize()
            delta = 0
            kwds['typename'] = t.name
            kwds['default'] = self._get_value(field.slot.defaultValue)
            decl = 'field.Primitive({offset}, Types.{typename}, default={default})'
        #
        elif which == 'bool':
            size = 0
            delta = 0
            byteoffset, bitoffset = divmod(field.slot.offset, 8)
            kwds['byteoffset'] = byteoffset
            kwds['bitoffset'] = bitoffset
            kwds['default'] = self._get_value(field.slot.defaultValue)
            decl = 'field.Bool({byteoffset}, {bitoffset}, default={default})'
        elif which == 'text':
            size = 8
            delta = data_size*8 # it's a pointer
            decl = 'field.String({offset})'
        #
        elif which == 'data':
            size = 8
            delta = data_size*8 # it's a pointer
            decl = 'field.Data({offset})'
        #
        elif which == 'struct':
            size = 8
            delta = data_size*8 # it's a pointer
            kwds['structname'] = self._get_typename(field.slot.type)
            decl = 'field.Struct({offset}, {structname})'
        #
        elif which == 'list':
            size = 8
            delta = data_size*8 # it's a pointer
            kwds['itemtype'] = self._get_typename(field.slot.type.list.elementType)
            decl = 'field.List({offset}, {itemtype})'
        #
        elif which == 'enum':
            size = 2
            delta = 0
            kwds['enumname'] = self._get_typename(field.slot.type)
            decl = 'field.Enum({offset}, {enumname})'
        #
        elif which == 'void':
            size = 0
            delta = 0
            decl = 'field.Void({offset})'
        #
        elif which == 'anyPointer':
            size = 8
            delta = data_size*8
            decl = 'field.AnyPointer({offset})'
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
        which = t.which()
        if hasattr(Types, which):
            return 'Types.%s' % which
        elif which == 'struct':
            return self._pyname(self.allnodes[t.struct.typeId])
        elif which == 'enum':
            return self._pyname(self.allnodes[t.enum.typeId])
        else:
            assert False

def generate_py_source(data):
    request = schema_capnp.CodeGeneratorRequest.from_bytes(data)
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
    data = open(sys.argv[1]).read()
    request, src = generate_py_source(data)
    print src

if __name__ == '__main__':
    main()
