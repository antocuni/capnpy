from __future__ import print_function
import py
import six
import keyword
from collections import defaultdict
from pypytools.codegen import Code
from six import PY3

from capnpy.compiler.util import as_identifier
from capnpy.convert_case import from_camel_case
from capnpy import schema
from capnpy import annotate
from capnpy.segment.segment import Segment, MultiSegment

# the following imports have side-effects, and augment the schema.* classes
# with emit() methods
import capnpy.compiler.request
import capnpy.compiler.node
import capnpy.compiler.struct_
import capnpy.compiler.field
import capnpy.compiler.enum
import capnpy.compiler.misc

class ModuleGenerator(object):

    def __init__(self, request, pyx, standalone, default_options, capnproto_version):
        self.request = request
        self.pyx = pyx
        self.standalone = standalone
        self.default_options = default_options
        self.capnproto_version = capnproto_version
        self.version_check = default_options.version_check
        self.code = Code(pyx=self.pyx)
        self.allnodes = {} # id -> node
        self.children = defaultdict(list) # nodeId -> nested nodes
        self._node_options = {} # node -> Options
        self.importnames = {} # filename -> import name
        self.extra_annotations = defaultdict(list) # obj -> [ann]
        self.field_override = {} # obj -> obj
        self.current_scope = None
        self.collect_nodes()
        self.compute_all_options()

    def collect_nodes(self):
        for node in self.request.nodes:
            self.allnodes[node.id] = node
            # roots have scopeId == 0, so they will be in children[0]
            self.children[node.scopeId].append(node)
        self.handle_py_groups()

    def options(self, node_or_field):
        return self._node_options[node_or_field.id]

    def compute_all_options(self):
        for f in self.request.requestedFiles:
            filenode = self.allnodes[f.id]
            filenode.compute_options(self, self.default_options)

    def compute_options_generic(self, entity, parent_opt):
        ann = self.has_annotation(entity, annotate.options)
        if ann:
            # this node was annotated with options
            opt = ann.annotation.value.struct.as_struct(annotate.Options)
            opt = parent_opt.combine(opt)
        else:
            opt = parent_opt
        self._node_options[entity.id] = opt

    def register_extra_annotation(self, obj, ann):
        self.extra_annotations[obj].append(ann.annotation)

    def register_field_override(self, origin, target):
        self.field_override[origin.id] = target

    def has_annotation(self, obj, anncls):
        try:
            annotations = self.extra_annotations.get(obj, [])
        except TypeError:
            # obj is not hashable, so we don't have extra_annotations
            annotations = []
        #
        if obj.annotations is not None:
            annotations += obj.annotations
        for ann in annotations:
            if ann.id == anncls.__capnpy_id__:
                # XXX: probably "annotation" should be taken by the
                # constructor
                res = anncls()
                res.annotation = ann
                res.target = obj
                return res
        return None

    def handle_py_groups(self):
        def register_py_group(struct_id, ann):
            field_void = ann.target
            node_group = schema.Node__Struct.from_group_annotation(
                self, struct_id, field_void, ann.annotation)
            node_id = node_group.id

            self.allnodes[node_id] = node_group
            self.children[struct_id].append(node_group)
            # Todo: we should populate `self.children[node_id]`

            # register a fake field
            field_group = schema.Field__Group.from_group_annotation(
                node_id, field_void)
            self.register_field_override(field_void, field_group)

        for struct_id, node in list(six.iteritems(self.allnodes)):
            if not node.is_struct():
                continue

            for field in node.get_struct_fields() or []:
                ann = self.has_annotation(field, annotate.group)
                if ann:
                    ann.check(self)
                    register_py_group(struct_id, ann)


    def w(self, *args, **kwargs):
        self.code.w(*args, **kwargs)

    def block(self, *args, **kwargs):
        return self.code.block(*args, **kwargs)

    def register_import(self, fname):
        name = py.path.local(fname).purebasename
        name = name.replace('+', 'PLUS')
        name = '_%s_capnp' % name
        if name in self.importnames.values():
            # avoid name clashes
            name = '%s_%s' % (name, len(self.filenames))
        self.importnames[fname] = name
        return name

    def generate(self):
        self.request.emit(self)
        return self.code.build()

    def _dump_node(self, node):
        def visit(node, deep=0):
            print('%s%s: %s' % (' ' * deep, node.which(), node.displayName))
            for child in self.children[node.id]:
                visit(child, deep+2)
        visit(node)

    def py_field_name(self, field):
        """
        Return the Python-side name of a field, with convert_case conversion
        applied
        """
        name = field.name
        name = as_identifier(name)
        if self.options(field).convert_case:
            name = from_camel_case(name)
        name = self._mangle_name(name)
        return name

    def capnp_field_name(self, field):
        """
        Return the capnproto-side name of a field. Always camelCase
        """
        name = field.name
        return as_identifier(name)

    def _mangle_name(self, name):
        if name in keyword.kwlist:
            return name + '_'
        return name

    def declare_enum(self, compile_name, name, capnpy_id, items):
        # this method cannot go on Node__Enum because it's also called by
        # Node__Struct (for __tag__)
        items = list(map(repr, items))
        ns = self.code.new_scope()
        ns.name = compile_name
        ns.capnpy_id = capnpy_id
        ns.members = "(%s,)" % (', '.join(items))
        ns.prebuilt = [ns.format('{name}({i})', i=i)
                       for i in range(len(items))]
        ns.prebuilt = ', '.join(ns.prebuilt)
        ns.prebuilt = ns.format('({prebuilt},)')
        with ns.block("{cdef class} {name}(_BaseEnum):"):
            ns.w("__capnpy_id__ = {capnpy_id}")
            ns.w("__members__ = {members}")
            #
            # define the _new staticmethod, to create new instances.
            if self.pyx:
                # on CPython, make a tuple of prebuilt instances for the
                # statically known values
                ns.w("@staticmethod")
                with ns.block('cdef _new(long x, __prebuilt={prebuilt}):') as ns:
                    ns.ww("""
                        try:
                            return __prebuilt[x]
                        except IndexError:
                            return {name}(x)
                    """)

                # The following is a hack so that other module can use it via import.
                ns.w("@staticmethod")
                with ns.block('def _new_hack(long x, __prebuilt={prebuilt}):') as ns:
                    ns.ww("""
                        try:
                            return __prebuilt[x]
                        except IndexError:
                            return {name}(x)
                    """)
            else:
                # on PyPy, always create a new object, so that the JIT will be
                # able to make it virtual
                ns.w("@staticmethod")
                with ns.block('def _new(x):') as ns:
                    ns.w('return {name}(x)')
        ns.w("_fill_enum({name})")

    def declare_const(self, clsname, s, segment=None):
        """
        Declare a const from a given segment.

        WARNING: this will dump the WHOLE segment of "s". If s is contained in
        only a small part of the segment, you might want to call .compact() on
        it before calling declare_const()
        """
        if segment is None:
            if isinstance(s._seg, MultiSegment):
                segment = '_MultiSegment({buf!r}, {offsets!r})'.format(
                    buf=s._seg.buf,
                    offsets=s._seg.segment_offsets)
            elif isinstance(s._seg, Segment):
                segment = '_Segment({buf!r})'.format(buf=s._seg.buf)
            else:
                assert False, "Unknown segment type"
        #
        return '{name}.from_buffer({seg}, {offset}, {data_size}, {ptrs_size})'.format(
            name=clsname,
            seg=segment,
            offset=s._data_offset,
            data_size=s._data_size,
            ptrs_size=s._ptrs_size)

    def def_property(self, ns, name, src):
        if self.pyx:
            with ns.block('property {name}:', name=name):
                with ns.block('def __get__(self):'):
                    ns.ww(src)
        else:
            ns.w('@property')
            with ns.block('def {name}(self):', name=name):
                ns.ww(src)
        ns.w()
