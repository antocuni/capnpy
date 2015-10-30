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
        m.declare_imports(f)
        m.w("")
        #
        # first of all, we emit all the non-structs and "predeclare" all the
        # structs
        structs = []
        children = m.children[node.id]
        for child in children:
            which = child.which()
            if which == schema.Node.__tag__.struct:
                m.declare_struct(child)
                structs.append(child)
            elif which == schema.Node.__tag__.enum:
                m.visit_enum(child)
            elif which == schema.Node.__tag__.annotation:
                # annotations are simply ignored for now
                pass
            else:
                assert False, 'Unkown node type: %s' % which
        #
        # then, we emit the body of all the structs we declared earlier
        for child in structs:
            m.visit_struct(child)
        #
        m.w("")
        m.w("try:")
        m.w("    import %s # side effects" % m.extname)
        m.w("except ImportError:")
        m.w("    pass")
