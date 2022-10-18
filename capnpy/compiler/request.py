import py
from datetime import datetime
from six import PY3
import capnpy
from capnpy import schema
from capnpy.type import Types
from capnpy.compiler.util import as_identifier
from capnpy import annotate


@schema.CodeGeneratorRequest.__extend__
class CodeGeneratorRequest:

    def emit(self, m):
        assert len(self.requestedFiles) == 1
        self.requestedFiles[0].emit(m)


@schema.CodeGeneratorRequest.RequestedFile.__extend__
class RequestedFile:

    def emit(self, m):
        m.modname = py.path.local(as_identifier(self.filename)).purebasename
        if not PY3:
            m.modname = m.modname.encode('utf-8')
        m.tmpname = '%s_tmp' % m.modname
        m.code.global_scope.extname = '%s_extended' % m.modname
        #
        # some lines need to be different when in pyx mode: here we define
        # some global kwarg which are "turned off" when in pure python mode
        if m.pyx:
            # pyx mode
            m.code.global_scope.cimport = 'cimport'
            m.code.global_scope.cpdef = 'cpdef'
            m.code.global_scope.__dict__['cdef class'] = 'cdef class'
        else:
            m.code.global_scope.cimport = 'import'
            m.code.global_scope.cpdef = 'def'
            m.code.global_scope.__dict__['cdef class'] = 'class'
        #
        filenode = m.allnodes[self.id]
        assert filenode.is_file()
        m.current_scope = filenode
        m.w("# THIS FILE HAS BEEN GENERATED AUTOMATICALLY BY capnpy")
        m.w("# do not edit by hand")
        m.w("# generated on %s" % datetime.now().strftime("%Y-%m-%d %H:%M"))
        m.w("# cython: language_level=2")
        m.w("")
        m.w("from capnpy {cimport} ptr as _ptr")
        m.w("from capnpy.struct_ {cimport} Struct as _Struct")
        m.w("from capnpy.struct_ {cimport} check_tag as _check_tag")
        m.w("from capnpy.struct_ import undefined as _undefined")
        m.w("from capnpy.enum import enum as _enum, fill_enum as _fill_enum")
        m.w("from capnpy.enum {cimport} BaseEnum as _BaseEnum")
        m.w("from capnpy.type import Types as _Types")
        m.w("from capnpy.segment.segment {cimport} Segment as _Segment")
        m.w("from capnpy.segment.segment {cimport} MultiSegment as _MultiSegment")
        m.w("from capnpy.segment.builder {cimport} SegmentBuilder as _SegmentBuilder")
        m.w("from capnpy.list {cimport} List as _List")
        m.w("from capnpy.list {cimport} PrimitiveItemType as _PrimitiveItemType")
        m.w("from capnpy.list {cimport} BoolItemType as _BoolItemType")
        m.w("from capnpy.list {cimport} TextItemType as _TextItemType")
        m.w("from capnpy.list {cimport} TextUnicodeItemType as _TextUnicodeItemType")
        m.w("from capnpy.list {cimport} StructItemType as _StructItemType")
        m.w("from capnpy.list {cimport} EnumItemType as _EnumItemType")
        m.w("from capnpy.list {cimport} VoidItemType as _VoidItemType")
        m.w("from capnpy.list {cimport} ListItemType as _ListItemType")
        m.w("from capnpy.anypointer import AnyPointer as _AnyPointer")
        m.w("from capnpy.util import text_bytes_repr as _text_bytes_repr")
        m.w("from capnpy.util import text_unicode_repr as _text_unicode_repr")
        m.w("from capnpy.util import data_repr as _data_repr")
        m.w("from capnpy.util import float32_repr as _float32_repr")
        m.w("from capnpy.util import float64_repr as _float64_repr")
        m.w("from capnpy.util import extend_module_maybe as _extend_module_maybe")
        m.w("from capnpy.util import check_version as _check_version")
        m.w("from capnpy.util import encode_maybe as _encode_maybe")
        #
        if m.pyx:
            m.w("from capnpy cimport _hash")
            all_types = [t.name for t in Types.__all__ if t is not Types.text]
            all_types += ['text_bytes', 'text_unicode']
            for tname in all_types:
                name = '%s_list_item_type' % tname
                m.w("from capnpy.list {cimport} {name} as _{name}", name=name)
        if m.pyx and not m.standalone:
            # load the compiler from the outside. See the comment in
            # _compile_pyx for a detailed explanation
            m.w('from %s import __compiler, __schema__' % m.tmpname)
        #
        m.w('__capnpy_id__ = {id:#x}', id=self.id)
        m.w('__capnpy_version__ = {version!r}', version=capnpy.__version__)
        m.w('__capnproto_version__ = {version!r}', version=m.capnproto_version)
        if m.version_check:
            m.w('_check_version(__name__, __capnpy_version__)')
        else:
            m.w('# schema compiled with --no-version-check, skipping the call to _check_version')

        self._declare_imports(m)
        if m.options(filenode).include_reflection_data:
            self._emit_reflection_data(m)
        else:
            m.w('# not including reflection data')
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
        if m.standalone:
            m.w('_extend_module_maybe(globals(), modname=__name__)')
        else:
            m.w('_extend_module_maybe(globals(), filename=__schema__)')
        m.w()

    def _declare_imports(self, m):
        for imp in self.imports:
            ns = m.code.new_scope()
            try:
                filenode = m.allnodes[imp.id]
            except KeyError:
                # this means that the file was imported but not used
                # anywhere. Simply ignore it
                continue
            fname = as_identifier(filenode.displayName)
            ns.importname = m.register_import(fname)
            ns.fullpath = as_identifier(imp.name)
            if ns.fullpath == '/capnp/c++.capnp':
                # ignore this file as it's useless for python
                continue
            elif m.standalone:
                assert ns.fullpath.endswith('.capnp')
                ns.modname = ns.fullpath.lstrip('/')[:-6].replace('/', '.')
                ns.w('import {modname} as {importname}')
            else:
                ns.pyx = m.pyx
                ns.w('{importname} = __compiler.load_schema(importname="{fullpath}", pyx={pyx})')

    def _emit_reflection_data(self, m):
        ns = m.code.new_scope()
        ns.modname = m.modname
        ns.request = m.declare_const('_CodeGeneratorRequest', m.request)
        ns.default_options = m.declare_const('_Options', m.default_options)
        ns.pyx = m.pyx
        ns.ww("""
            from capnpy.schema import CodeGeneratorRequest as _CodeGeneratorRequest
            from capnpy.annotate import Options as _Options
            from capnpy.reflection import ReflectionData as _ReflectionData
            class _{modname}_ReflectionData(_ReflectionData):
                request = {request}
                default_options = {default_options}
                pyx = {pyx}
            _reflection_data = _{modname}_ReflectionData()
        """)
