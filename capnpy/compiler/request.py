import py
from datetime import datetime
from capnpy import schema

@schema.CodeGeneratorRequest.__extend__
class CodeGeneratorRequest:

    def emit(self, m):
        for node in self.nodes:
            m.allnodes[node.id] = node
            # roots have scopeId == 0, so they will be in children[0]
            m.children[node.scopeId].append(node)
        #
        assert len(self.requestedFiles) == 1
        self.requestedFiles[0].emit(m)


@schema.CodeGeneratorRequest.RequestedFile.__extend__
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
            m.w("enum = staticmethod(enum)")
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
