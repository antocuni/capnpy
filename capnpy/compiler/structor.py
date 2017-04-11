"""
Structor -> struct ctor -> struct construtor :)
"""

import struct
from capnpy.type import Types
from capnpy.schema import Field, Type, Value
from capnpy.compiler.fieldtree import FieldTree, Node

class Structor(object):
    """
    Create a struct constructor.

    Some terminology:
      - argnames: the name of arguments taken by the ctor
      - params: [(argname, default)], for each argname in argnames
    """

    def __init__(self, m, struct, fields):
        self.m = m
        self.struct = struct
        self.data_size = struct.dataWordCount
        self.ptrs_size = struct.pointerCount
        self.fieldtree = FieldTree(m, self.struct)
        self.argnames, self.params = self.fieldtree.get_args_and_params()

    def slot_offset(self, f):
        offset = f.slot.offset * f.slot.get_size()
        if f.slot.type.is_pointer():
            offset += self.data_size*8
        return offset

    def emit(self):
        ## generate a constructor which looks like this
        ## @staticmethod
        ## def __new(x=0, y=0, z=None):
        ##     builder = _SegmentBuilder()
        ##     pos = builder.allocate(24)
        ##     builder.write_int64(pos + 0, x)
        ##     builder.write_int64(pos + 8, y)
        ##     builder.alloc_text(pos + 16, z)
        ##     return builder.as_string()
        #
        # the parameters have the same order as fields
        code = self.m.code
        argnames = self.argnames
        if len(argnames) != len(set(argnames)):
            raise ValueError("Duplicate field name(s): %s" % argnames)
        #
        code.w('@staticmethod')
        with code.cdef_('__new', self.params) as ns:
            ns.length = (self.data_size + self.ptrs_size)*8
            ns.cdef_var('_SegmentBuilder', 'builder')
            ns.cdef_var('long', 'pos')
            ns.w('builder = _SegmentBuilder()')
            ns.w('pos = builder.allocate({length})')
            for union in self.fieldtree.all_unions():
                ns.w('{union}__curtag = None', union=union.varname)
            for node in self.fieldtree.children:
                self.handle_node(node)
            ns.w('return builder.as_string()')

    def handle_node(self, node):
        if node.f.is_part_of_union():
            ns = self.m.code.new_scope()
            ns.varname = node.varname
            ns.union = node.parent.union.varname
            ns.offset = node.parent.union.offset
            ns.tagval = node.f.discriminantValue
            ns.tagname = self.m._field_name(node.f)
            ns.ifmt  = 'ord(%r)' % Types.int16.fmt
            with ns.block('if {varname} is not _undefined:'):
                ns.w('{union}__curtag = _check_tag({union}__curtag, {tagname!r})')
                ns.w('builder.write_int16({offset}, {tagval})')
                self._handle_node(node)
        else:
            self._handle_node(node)

    def _handle_node(self, node):
        f = node.f
        if f.is_nullable(self.m):
            self.handle_nullable(node)
        elif f.is_group():
            self.handle_group(node)
        elif f.is_text():
            self.handle_text(node)
        elif f.is_data():
            self.handle_data(node)
        elif f.is_struct():
            self.handle_struct(node)
        elif f.is_list():
            self.handle_list(node)
        elif f.is_primitive() or f.is_enum():
            self.handle_primitive(node)
        elif f.is_bool():
            self.handle_bool(node)
        elif f.is_void():
            pass # nothing to do
        else:
            self.m.code.w("raise NotImplementedError('Unsupported field type: {f}')",
                          f=node.f.shortrepr())

    def handle_group(self, node):
        # def __init__(self, position, ...):
        #     ...
        #     position_x, position_y = position
        #     builder.write_...(..., position_x)
        #     builder.write_...(..., position_y)
        #     ...
        #
        # 1. unpack the tuple into various indepented variables
        ns = self.m.code.new_scope()
        ns.group = node.varname
        argnames = [child.varname for child in node.children]
        ns.args = self.m.code.args(argnames)
        ns.w('{args}, = {group}')
        #
        # 2. recursively handle all the children
        for child in node.children:
            self.handle_node(child)

    def handle_nullable(self, node):
        # def __init__(self, ..., x, ...):
        #     ...
        #     if x is None:
        #         x_is_null = 1
        #         x_value = 0
        #     else:
        #         x_is_null = 0
        #         x_value = x
        #
        ns = self.m.code.new_scope()
        ns.fname = node.varname
        ns.ww(
        """
            if {fname} is None:
                {fname}_is_null = 1
                {fname}_value = 0
            else:
                {fname}_is_null = 0
                {fname}_value = {fname}
        """)
        for child in node.children:
            self.handle_node(child)

    def handle_text(self, node):
        self.m.code.w('builder.alloc_text(pos + {offset}, {arg})',
                      arg=node.varname, offset=self.slot_offset(node.f))

    def handle_data(self, node):
        self.m.code.w('builder.alloc_data(pos + {offset}, {arg})',
                      arg=node.varname, offset=self.slot_offset(node.f))

    def handle_struct(self, node):
        ## @staticmethod
        ## def __new(x=0, y=<some struct>):
        ##     builder = _SegmentBuilder()
        ##     pos = builder.allocate(16)
        ##     ...
        ##     builder.copy_from_struct(pos+8, SomeStruct, y)
        ns = self.m.code.new_scope()
        ns.fname = node.varname
        ns.offset = self.slot_offset(node.f)
        ns.structname = node.f.slot.type.runtime_name(self.m)
        ns.w('builder.copy_from_struct(pos + {offset}, {structname}, {fname})')

    def handle_list(self, node):
        ns = self.m.code.new_scope()
        ns.fname = node.varname
        ns.offset = self.slot_offset(node.f)
        t = node.f.slot.type.list.elementType
        ns.list_item_type = t.list_item_type(self.m)
        ns.w('builder.copy_from_list(pos + {offset}, {list_item_type}, {fname})')

    def handle_primitive(self, node):
        ns = self.m.code.new_scope()
        ns.arg = node.varname
        if node.f.slot.hadExplicitDefault:
            ns.default_ = node.f.slot.defaultValue.as_pyobj()
            ns.w('{arg} ^= {default_}')
        #
        ns.type = node.f.slot.get_typename()
        ns.offset = self.slot_offset(node.f)
        ns.w('builder.write_{type}(pos + {offset}, {arg})')

    def handle_bool(self, node):
        ns = self.m.code.new_scope()
        ns.arg = node.varname
        ns.byteoffset, ns.bitoffset = divmod(node.f.slot.offset, 8)
        if node.f.slot.hadExplicitDefault:
            ns.default_ = node.f.slot.defaultValue.as_pyobj()
            ns.w('{arg} ^= {default_}')
        ns.w('builder.write_bool({byteoffset}, {bitoffset}, {arg})')
