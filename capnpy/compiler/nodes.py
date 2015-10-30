import py
from datetime import datetime
from capnpy import schema
from capnpy.util import extend

@extend(schema.CodeGeneratorRequest)
class CodeGeneratorRequest:

    def emit(self, m):
        for node in self.nodes:
            m.allnodes[node.id] = node
            # roots have scopeId == 0, so they will be in children[0]
            m.children[node.scopeId].append(node)
        #
        assert len(self.requestedFiles) == 1
        self.requestedFiles[0].emit(m)


@extend(schema.CodeGeneratorRequest.RequestedFile)
class RequestedFile:

    def emit(self, m):
        m.modname = py.path.local(self.filename).purebasename
        m.extname = '%s_extended' % m.modname
        m.tmpname = '%s_tmp' % m.modname
        #
        node = m.allnodes[self.id]
        m.current_scope = node
        m.w("# THIS FILE HAS BEEN GENERATED AUTOMATICALLY BY capnpy")
        m.w("# do not edit by hand")
        m.w("# generated on %s" % datetime.now().strftime("%Y-%m-%d %H:%M"))
        m.w("# input files: ")
        for f in m.request.requestedFiles:
            m.w("#   - %s" % self.filename)
        m.w("")
        with m.block("class __(object):"):
            m.w("from capnpy.struct_ import Struct, undefined")
            m.w("from capnpy import field")
            m.w("from capnpy.enum import enum")
            m.w("from capnpy.blob import Types")
            m.w("from capnpy.builder import StructBuilder")
            m.w("from capnpy.list import PrimitiveList, StructList, StringList")
            m.w("from capnpy.util import extend")
            m.w("enum = staticmethod(enum)")
            m.w("extend = staticmethod(extend)")
        #
        if m.pyx:
            # load the compiler from the outside. See the comment in
            # _compile_pyx for a detailed explanation
            m.w('from %s import __compiler' % m.tmpname)
        #
        f._declare_imports(m)
        m.w("")
        #
        # visit the children in two passes: first the declaration, then the
        # definition
        children = m.children[node.id]
        for child in children:
            child.emit_declaration(m)
        for child in children:
            child.emit_definition(m)
        #
        m.w("")
        m.w("try:")
        m.w("    import %s # side effects" % m.extname)
        m.w("except ImportError:")
        m.w("    pass")

    def _declare_imports(self, m):
        for imp in self.imports:
            fname = imp.name
            m.w('{decl_name} = __compiler.load_schema("{fname}")',
                decl_name = m._pyname_for_file(fname),
                fname = fname)



@extend(schema.Node)
class Node:

    def emit_declaration(self, m):
        which = self.which()
        if which == schema.Node.__tag__.struct:
            self._declare_struct(m)
        elif which == schema.Node.__tag__.enum:
            m.visit_enum(self)
        elif which == schema.Node.__tag__.annotation:
            # annotations are simply ignored for now
            pass
        else:
            assert False, 'Unkown node type: %s' % which

    def emit_definition(self, m):
        which = self.which()
        if which == schema.Node.__tag__.struct:
            m.visit_struct(self)
        else:
            pass

    def _declare_struct(self, m):
        name = m._shortname(self)
        with m.block("class %s(__.Struct):" % name):
            for child in m.children[self.id]:
                if child.which() == schema.Node.__tag__.struct:
                    child.emit_declaration(m)
            m.w("pass")

