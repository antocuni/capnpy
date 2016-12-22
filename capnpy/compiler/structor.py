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
        self.fieldtree = FieldTree(m, self.struct, union_default='_undefined')
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
        ##     builder = _MutableBuilder(24)
        ##     builder.set(ord('q', 0, x)
        ##     builder.set(ord('q', 8, y)
        ##     builder.alloc_text(16, z)
        ##     return builder.build()
        #
        # the parameters have the same order as fields
        code = self.m.code
        argnames = self.argnames
        if len(argnames) != len(set(argnames)):
            raise ValueError("Duplicate field name(s): %s" % argnames)
        code.w('@staticmethod')
        with code.def_('__new', self.params) as ns:
            ns.total_length = (self.data_size + self.ptrs_size)*8
            ns.w('builder = _MutableBuilder({total_length})')
            for node in self.fieldtree.iterfields(): #children:
                self.handle_node(node)
            ns.w('return builder.build()')

    def handle_anonymous_union(self, node):
        code = self.m.code
        code.w('__which__ = 0')
        code.w('_curtag = None')
        for child in node.fields:
            ns = code.new_scope()
            ns.varname = child.varname
            ns.tagval = child.f.discriminantValue
            ns.tagname = self.m._field_name(child.f)
            with ns.block('if {varname} is not _undefined:'):
                ns.w('__which__ = {tagval}')
                ns.w('_curtag = _check_tag(_curtag, {tagname!r})')
                self.handle_node(child)
        #
        ns.offset = node.struct.discriminantOffset * 2
        ns.ifmt  = 'ord(%r)' % Types.int16.fmt
        ns.w('builder.set({ifmt}, {offset}, __which__)')

    def handle_node(self, node):
        if node.is_anonymous_union():
            self.handle_anonymous_union(node)
            return
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
        elif f.is_void():
            pass # nothing to do
        else:
            code.w("raise NotImplementedError('Unsupported field type: {f}')",
                   f=node.f.shortrepr())

    def handle_group(self, node):
        # def __init__(self, position, ...):
        #     ...
        #     position_x, position_y = position
        #     builder.set(..., position_x)
        #     builder.set(..., position_y)
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
        self.m.code.w('builder.alloc_text({offset}, {arg})',
                      arg=node.varname, offset=self.slot_offset(node.f))

    def handle_data(self, node):
        self.m.code.w('builder.alloc_data({offset}, {arg})',
                      arg=node.varname, offset=self.slot_offset(node.f))

    def handle_struct(self, node):
        offset = self.slot_offset(node.f)
        structname = node.f.slot.type.runtime_name(self.m)
        self.m.code.w('builder.alloc_struct({offset}, {structname}, {arg})',
                      arg=node.varname, offset=offset, structname=structname)

    def handle_list(self, node):
        ns = self.m.code.new_scope()
        ns.fname = node.varname
        ns.offset = self.slot_offset(node.f)
        itemtype = node.f.slot.type.list.elementType
        ns.itemtype = itemtype.runtime_name(self.m)
        #
        if itemtype.is_primitive():
            ns.listcls = '_PrimitiveList'
        elif itemtype.is_text():
            ns.listcls = '_StringList'
        elif itemtype.is_struct():
            ns.listcls = '_StructList'
        else:
            raise ValueError('Unknown item type: %s' % item_type)
        #
        ns.w('builder.alloc_list({offset}, {listcls}, {itemtype}, {fname})')

    def handle_primitive(self, node):
        ns = self.m.code.new_scope()
        ns.arg = node.varname
        if node.f.slot.hadExplicitDefault:
            ns.default_ = node.f.slot.defaultValue.as_pyobj()
            ns.w('{arg} ^= {default_}')
        #
        ns.ifmt = "ord(%r)" % node.f.slot.get_fmt()
        ns.offset = self.slot_offset(node.f)
        ns.w('builder.set({ifmt}, {offset}, {arg})')
