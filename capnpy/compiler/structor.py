"""
Structor -> struct ctor -> struct construtor :)
"""

import struct
from capnpy.schema import Field, Type, Value
from capnpy.compiler.fieldtree import FieldTree, Node

class Unsupported(Exception):
    pass

class Structor(object):
    """
    Create a struct constructor.

    Some terminology:
      - argnames: the name of arguments taken by the ctor
      - params: [(argname, default)], for each argname in argnames
    """

    def __init__(self, m, name, data_size, ptrs_size, fields,
                 tag_offset=None, tag_value=None):
        self.m = m
        self.name = name
        self.fieldtree = FieldTree(m, fields)
        self.tag_value = tag_value
        self._init_layout(data_size, ptrs_size, tag_offset)
        self._init_args()

    def _init_layout(self, data_size, ptrs_size, tag_offset):
        self.layout = Layout(self.m, data_size, ptrs_size, tag_offset)
        try:
            self.layout.add_tree(self.fieldtree)
        except Unsupported as e:
            self._unsupported = e.message
        else:
            self._unsupported = None

    def _init_args(self):
        self.argnames = []
        self.params = []
        if self._unsupported:
            return
        #
        # the arguments taken by the ctor corresponds to the varname of the
        # *first* level of the tree
        for node in self.fieldtree.children:
            self.argnames.append(node.varname)
            self.params.append((node.varname, node.default))

    def declare(self, code):
        if self._unsupported is not None:
            return self._decl_unsupported(code)
        else:
            return self._decl_ctor(code)

    def _decl_unsupported(self, code):
        code.w('@staticmethod')
        with code.def_(self.name, self.argnames, '*args', '**kwargs'):
            code.w('raise NotImplementedError({msg})', msg=repr(self._unsupported))

    def _decl_ctor(self, code):
        ## generate a constructor which looks like this
        ## @staticmethod
        ## def ctor(x=0, y=0, z=None):
        ##     builder = _StructBuilder('qqq')
        ##     z = builder.alloc_text(16, z)
        ##     buf = builder.build(x, y)
        ##     return buf
        #
        # the parameters have the same order as fields
        argnames = self.argnames

        if len(argnames) != len(set(argnames)):
            raise ValueError("Duplicate field name(s): %s" % argnames)
        code.w('@staticmethod')
        with code.def_(self.name, self.params):
            code.w('builder = _StructBuilder({fmt})',
                   fmt=repr(self.layout.fmt))
            if self.tag_value is not None:
                code.w('__which__ = {tag_value}', tag_value=int(self.tag_value))
            #
            for node in self.fieldtree.allnodes():
                f = node.f
                if f.is_nullable(self.m):
                    self.handle_nullable(code, node)
                elif f.is_group():
                    self.handle_group(code, node)
                elif f.is_text():
                    self.handle_text(code, node)
                elif f.is_data():
                    self.handle_data(code, node)
                elif f.is_struct():
                    self.handle_struct(code, node)
                elif f.is_list():
                    self.handle_list(code, node)
                elif f.is_primitive() or f.is_enum():
                    self.handle_primitive(code, node)
                elif f.is_void():
                    pass # nothing to do
                else:
                    code.w("raise NotImplementedError('Unsupported field type: {f}')",
                           f=node.f.shortrepr())
            #
            buildnames = [n.varname for n in self.layout.slots
                          if not n.f.is_void()]
            code.w('buf =', code.call('builder.build', buildnames))
            code.w('return buf')

    def handle_group(self, code, node):
        ns = code.new_scope()
        ns.group = node.varname
        argnames = [child.varname for child in node.children
                    if not child.f.is_void()] # XXX: handle void more consistently
        ns.args = code.args(argnames)
        ns.w('{args}, = {group}')

    def handle_nullable(self, code, node):
        # def __init__(self, ..., x, ...):
        #     ...
        #     if x is None:
        #         x_is_null = 1
        #         x_value = 0
        #     else:
        #         x_is_null = 0
        #         x_value = x
        #
        ns = code.new_scope()
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

    def handle_text(self, code, node):
        code.w('{arg} = builder.alloc_text({offset}, {arg})',
               arg=node.varname, offset=self.layout.slot_offset(node.f))

    def handle_data(self, code, node):
        code.w('{arg} = builder.alloc_data({offset}, {arg})',
               arg=node.varname, offset=self.layout.slot_offset(node.f))

    def handle_struct(self, code, node):
        offset = self.layout.slot_offset(node.f)
        structname = node.f.slot.type.runtime_name(self.m)
        code.w('{arg} = builder.alloc_struct({offset}, {structname}, {arg})',
               arg=node.varname, offset=offset, structname=structname)

    def handle_list(self, code, node):
        ns = code.new_scope()
        ns.fname = node.varname
        ns.offset = self.layout.slot_offset(node.f)
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
        ns.w('{fname} = builder.alloc_list({offset}, {listcls}, {itemtype}, {fname})')

    def handle_primitive(self, code, node):
        if node.f.slot.hadExplicitDefault:
            ns = code.new_scope()
            ns.arg = node.varname
            ns.default_ = node.f.slot.defaultValue.as_pyobj()
            ns.w('{arg} ^= {default_}')



class Layout(object):
    """
    Low level layout of a struct
    """

    def __init__(self, m, data_size, ptrs_size, tag_offset):
        self.m = m
        self.data_size = data_size
        self.ptrs_size = ptrs_size
        self.fmt = None    # computed later
        self.slots = []
        #
        if tag_offset is not None:
            # add a field to represent the tag
            tag_offset /= 2 # from bytes to multiple of int16
            f = Field.new_slot('__which__', tag_offset,
                               Type.new_int16(),
                               Value.new_int16(0))
            node = Node(m, f, prefix=None)
            self.slots.append(node)

    def add_tree(self, tree):
        self.slots += tree.allslots()
        self._finish()

    def _finish(self):
        """
        Compute the format string and sort the slots in order of offset
        """
        total_length = (self.data_size + self.ptrs_size)*8
        fmt = ['x'] * total_length

        def set(offset, t):
            fmt[offset] = t
            size = struct.calcsize(t)
            for i in range(offset+1, offset+size):
                fmt[i] = None

        self.slots.sort(key=lambda node: self.slot_offset(node.f))
        for node in self.slots:
            f = node.f
            if not f.is_slot() or f.slot.type.is_bool():
                raise Unsupported('Unsupported field type: %s' % f.shortrepr())
            elif f.is_void():
                continue
            set(self.slot_offset(f), f.slot.get_fmt())
        #
        # remove all the Nones
        fmt = [ch for ch in fmt if ch is not None]
        fmt = ''.join(fmt)
        assert struct.calcsize(fmt) == total_length
        self.fmt = fmt

    def slot_offset(self, f):
        offset = f.slot.offset * f.slot.get_size()
        if f.slot.type.is_pointer():
            offset += self.data_size*8
        return offset
