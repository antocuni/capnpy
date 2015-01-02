import py
import types
from datetime import datetime
import subprocess
from contextlib import contextmanager
from capnpy.type import Types

# XXX: this is temporarily using pycapnp to bootstrap: we will kill the
# dependency as soon as we can generate our own schema_capnp.py
import capnp
import schema_capnp

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
        self.structs = {} # id -> structName

    def generate(self):
        self.visit_request(self.request)
        return self.builder.build()

    def w(self, s):
        self.builder.writeline(s)

    def block(self, s):
        return self.builder.indent(s)

    def visit_request(self, request):
        self.w("# THIS FILE HAS BEEN GENERATED AUTOMATICALLY BY capnpy")
        self.w("# do not edit by hand")
        self.w("# generated on %s" % datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.w("# input files: ")
        for f in request.requestedFiles:
            self.w("#   - %s" % f.filename)
        self.w("")
        self.w("from capnpy.struct_ import Struct")
        self.w("from capnpy import field")
        self.w("from capnpy.blob import Types")
        self.w("")
        
        for node in request.nodes:
            self.visit_node(node)

    def visit_node(self, node):
        which = node.which()
        if which == 'struct':
            self.visit_struct(node)
        elif which == 'file':
            pass
        else:
            assert False, 'Unkown node type: %s' % which

    def visit_struct(self, node):
        name = node.displayName[node.displayNamePrefixLength:]
        self.structs[node.id] = name
        with self.block("class %s(Struct):" % name):
            data_size = node.struct.dataWordCount
            ptrs_size = node.struct.pointerCount
            self.w("__data_size__ = %d" % data_size)
            self.w("__ptrs_size__ = %d" % ptrs_size)            
            self.w("")
            if node.struct.discriminantCount:
                pass # XXX
            if node.struct.isGroup:
                pass # XXX
            for field in node.struct.fields:
                self.visit_field(field, data_size, ptrs_size)
        self.w("")

    def visit_field(self, field, data_size, ptrs_size):
        assert field.which() == 'slot'
        assert not field.slot.hadExplicitDefault
        kwds = {}
        which = field.slot.type.which()
        if Types.is_primitive(which):
            t = getattr(Types, which)
            size = t.calcsize()
            delta = 0
            kwds['typename'] = t.name
            decl = 'field.Primitive({offset}, Types.{typename})'
        #
        elif which == 'text':
            size = 8
            delta = data_size*8 # it's a pointer
            decl = 'field.String({offset})'
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
        else:
            raise ValueError('Unknown type: %s' % field.slot.type)
        #
        kwds['offset'] = delta + field.slot.offset*size
        kwds['name'] = field.name
        line = '{name} = ' + decl
        self.w(line.format(**kwds))

    def _get_typename(self, t):
        which = t.which()
        if hasattr(Types, which):
            return 'Types.%s' % which
        elif which == 'struct':
            return self.structs[t.struct.typeId]
        else:
            assert False


def compile_file(filename):
    data = _capnp_compile(filename)
    request = schema_capnp.CodeGeneratorRequest.from_bytes(data)
    gen = FileGenerator(request)
    src = gen.generate()
    src = py.code.Source(src)
    mod = types.ModuleType(filename.purebasename)
    mod.__file__ = str(filename)
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
