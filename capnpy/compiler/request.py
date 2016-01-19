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
        # some lines need to be different when in pyx mode: here we define
        # some global kwarg which are "turned off" when in pure python mode
        if m.pyx:
            # pyx mode
            m.code.global_scope.cimport = 'cimport'
            m.code.global_scope.__dict__['cdef class'] = 'cdef class'
        else:
            m.code.global_scope.cimport = 'import'
            m.code.global_scope.__dict__['cdef class'] = 'class'
        #
        filenode = m.allnodes[self.id]
        assert filenode.is_file()
        m.current_scope = filenode
        m.w("# THIS FILE HAS BEEN GENERATED AUTOMATICALLY BY capnpy")
        m.w("# do not edit by hand")
        m.w("# generated on %s" % datetime.now().strftime("%Y-%m-%d %H:%M"))
        m.w("# input files: ")
        for f in m.request.requestedFiles:
            m.w("#   - %s" % self.filename)
        m.w("")
        m.w("from capnpy.struct_ {cimport} Struct as _Struct")
        m.w("from capnpy.struct_ import undefined as _undefined")
        m.w("from capnpy import field as _field")
        m.w("from capnpy.enum import enum as _enum")
        m.w("from capnpy.blob import Types as _Types")
        m.w("from capnpy.builder import StructBuilder as _StructBuilder")
        m.w("from capnpy.list import PrimitiveList as _PrimitiveList")
        m.w("from capnpy.list import StructList as _StructList")
        m.w("from capnpy.list import StringList as _StringList")
        #
        if m.pyx:
            m.w("from capnpy.unpack cimport unpack_primitive")
            # load the compiler from the outside. See the comment in
            # _compile_pyx for a detailed explanation
            m.w('from %s import __compiler' % m.tmpname)
        #
        f._declare_imports(m)
        m.w("")
        #
        # visit the children in two passes: first the declaration, then the
        # definition
        children = m.children[filenode.id]
        m.w("#### FORWARD DECLARATIONS ####")
        m.w()
        for child in children:
            child.emit_declaration(m)
        m.w()
        m.w("#### DEFINITIONS ####")
        m.w()
        for child in children:
            child.emit_definition(m)
        #
        for child in children:
            child.emit_reference_as_child(m)
        #
        m.w()
        for child in children:
            child.emit_delete_nested_from_globals(m)
        m.w()
        m.w("try:")
        m.w("    import %s # side effects" % m.extname)
        m.w("except ImportError:")
        m.w("    pass")

    def _declare_imports(self, m):
        for imp in self.imports:
            filenode = m.allnodes[imp.id]
            fname = filenode.displayName
            importname = m.register_import(fname)
            fullpath = imp.name
            m.w('{importname} = __compiler.load_schema("{fullpath}")',
                importname = importname,
                fullpath = fullpath)
