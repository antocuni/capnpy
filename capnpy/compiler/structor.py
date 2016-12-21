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

    The **private** constructor is a static method which build and return a
    buffer. The **public** constructor is a classmethod which return a fully
    constructed object around the buffer returned by the private constructor::

        # private constructor
        @staticmethod
        def __new(x, y):
            ...
            return builder.build(x, y)

        # public constructor
        @classmethod
        def new(cls, x, y):
            buf = cls.__new(x, y)
            return cls.from_buffer(buf, ...)
    """

    def __init__(self, m, suffix, data_size, ptrs_size, fields, tag_offset=None):
        self.m = m
        self.name = 'new'
        if suffix:
            self.name += '_' + suffix
        self.private_name = '__' + self.name
        self.fieldtree = FieldTree(m, fields, union_default='_undefined')
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
        if self._unsupported:
            self.argnames = []
            self.params = []
            return
        self.argnames, self.params = self.fieldtree.get_args_and_params()

    def emit_public(self, code, ns):
        ns.w('@classmethod')
        with ns.def_(self.name, ['cls'] + self.params):
            call = code.call('cls.' + self.private_name, self.argnames)
            ns.w('buf = {call}', call=call)
            ns.w('return cls.from_buffer(buf, 0, {data_size}, {ptrs_size})')
        ns.w()

    def emit_private(self, code):
        if self._unsupported is not None:
            return self._emit_unsupported(code)
        else:
            return self._emit_private(code)

    def _emit_unsupported(self, code):
        code.w('@staticmethod')
        with code.def_(self.private_name, self.argnames, '*args', '**kwargs'):
            code.w('raise NotImplementedError({msg})', msg=repr(self._unsupported))

    def _emit_private(self, code):
        ## generate a constructor which looks like this
        ## @staticmethod
        ## def __new(x=0, y=0, z=None):
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
        with code.def_(self.private_name, self.params):
            code.w('builder = _MutableBuilder({l})', l=self.layout.total_length)
            allnodes = list(self.fieldtree.allnodes())
            std_nodes = [node for node in allnodes if not node.f.is_part_of_union()]
            union_nodes = [node for node in allnodes if node.f.is_part_of_union()]
            #
            # first, handle normal fields
            for node in std_nodes:
                self.handle_field(code, node)
            #
            # then, handle union fields (if any)
            if union_nodes:
                code.w('__which__ = 0')
                code.w('_curtag = None')
                for node in union_nodes:
                    ns = code.new_scope()
                    ns.varname = node.varname
                    ns.tagval = node.f.discriminantValue
                    ns.tagname = self.m._field_name(node.f)
                    with ns.block('if {varname} is not _undefined:'):
                        ns.w('__which__ = {tagval}')
                        ns.w('_curtag = _check_tag(_curtag, {tagname!r})')
                        self.handle_field(code, node)
                self.handle_field(code, self.layout.node_which)
            #
            code.w('return builder.build()')

    def handle_field(self, code, node):
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

    def handle_group(self, code, node):
        node.emit_unpack_group(code)

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
        code.w('builder.alloc_text({offset}, {arg})',
               arg=node.varname, offset=self.layout.slot_offset(node.f))

    def handle_data(self, code, node):
        code.w('builder.alloc_data({offset}, {arg})',
               arg=node.varname, offset=self.layout.slot_offset(node.f))

    def handle_struct(self, code, node):
        offset = self.layout.slot_offset(node.f)
        structname = node.f.slot.type.runtime_name(self.m)
        code.w('builder.alloc_struct({offset}, {structname}, {arg})',
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
        ns.w('builder.alloc_list({offset}, {listcls}, {itemtype}, {fname})')

    def handle_primitive(self, code, node):
        ns = code.new_scope()
        ns.arg = node.varname
        if node.f.slot.hadExplicitDefault:
            ns.default_ = node.f.slot.defaultValue.as_pyobj()
            ns.w('{arg} ^= {default_}')
        #
        ns.ifmt = "ord(%r)" % node.f.slot.get_fmt()
        ns.offset = self.layout.slot_offset(node.f) # XXX
        ns.w('builder.set({ifmt}, {offset}, {arg})')


class Layout(object):
    """
    Low level layout of a struct
    """

    def __init__(self, m, data_size, ptrs_size, tag_offset):
        self.m = m
        self.data_size = data_size
        self.ptrs_size = ptrs_size
        self.total_length = (self.data_size + self.ptrs_size)*8
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
            self.node_which = node
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
