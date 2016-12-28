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
        ##     builder = _Builder(24)
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
        #
        code.w('@staticmethod')
        with code.def_('__new', self.params) as ns:
            ns.total_length = (self.data_size + self.ptrs_size)*8
            ns.w('builder = _Builder({total_length})')
            for union in self.fieldtree.all_unions():
                ns.w('{union}__curtag = None', union=union.varname)
            for node in self.fieldtree.children:
                self.handle_node(node)
            ns.w('return builder.build()')

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
                ns.w('builder.set({ifmt}, {offset}, {tagval})')
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

    def handle_bool(self, node):
        ns = self.m.code.new_scope()
        ns.arg = node.varname
        ns.byteoffset, ns.bitoffset = divmod(node.f.slot.offset, 8)
        if node.f.slot.hadExplicitDefault:
            ns.default_ = node.f.slot.defaultValue.as_pyobj()
            ns.w('{arg} ^= {default_}')
        ns.w('builder.setbool({byteoffset}, {bitoffset}, {arg})')
