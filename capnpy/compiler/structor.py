"""
Structor -> struct ctor -> struct construtor :)
"""

import struct
from capnpy.schema import Field, Type
from capnpy.compiler.fieldtree import FieldTree

class Unsupported(Exception):
    pass

class Structor(object):
    """
    Create a struct constructor.

    Some terminology:

      - fields: the list of schema.Field objects, as it appears in
                schema.Node.struct

      - argnames: the name of arguments taken by the ctor

      - params: [(argname, default)], for each argname in argnames

      - llfields: flattened list of "low level fields", as they are used to
                  build the buffer.  Normally, each field corresponds to one
                  llfield, but each group field has many llfields

      - llnames: {llfield: llname}; the llname if the name of the variable
                 used to contain the value of each llfield. For llfields
                 inside groups, it is "groupname_fieldname".

    In case of groups, we generate code to map the single argname into the
    many llfields: this is called "unpacking"
    """

    _unsupported = None

    def __init__(self, m, name, data_size, ptrs_size, fields,
                 tag_offset=None, tag_value=None):
        self.m = m
        self.name = name
        self.fieldtree = FieldTree(m, fields)
        self.tag_value = tag_value
        self.argnames = []    # the arguments accepted by the ctor, in order
        self.params = []
        #
        self.layout = Layout(m, data_size, ptrs_size, tag_offset)
        try:
            self.layout.add_tree(self.fieldtree)
        except Unsupported as e:
            self.argnames = []
            self._unsupported = e.message
        #
        self.llname = self.layout.llname # XXX
        self.init_fields(fields)

    def init_fields(self, fields):
        defaults = []
        self.argnames = [self.m._field_name(f) for f in fields]
        for f in fields:
            if f.is_group():
                defaults.append('None') # XXX fixme
            else:
                default = f.slot.defaultValue.as_pyobj()
                defaults.append(str(default))

        assert len(self.argnames) == len(defaults)
        self.params = zip(self.argnames, defaults)

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
                    self.handle_nullable(code, f)
                elif f.is_group():
                    self.handle_group(code, f)
                elif f.is_text():
                    self.handle_text(code, f)
                elif f.is_data():
                    self.handle_data(code, f)
                elif f.is_struct():
                    self.handle_struct(code, f)
                elif f.is_list():
                    self.handle_list(code, f)
                elif f.is_primitive() or f.is_enum():
                    self.handle_primitive(code, f)
                elif f.is_void():
                    pass # nothing to do
                else:
                    code.w("raise NotImplementedError('Unsupported field type: {f}')",
                           f=f.shortrepr())
            #
            buildnames = [self.llname[f]
                          for f in self.layout.llfields
                          if not f.is_void()]
            code.w('buf =', code.call('builder.build', buildnames))
            code.w('return buf')

    def handle_group(self, code, f):
        group = self.m.allnodes[f.group.typeId]
        groupname = self.m._field_name(f)
        argnames = [self.llname[f] for f in group.struct.fields
                    if not f.is_void()]
        code.w('{args}, = {groupname}',
               args=code.args(argnames), groupname=groupname)

    def handle_nullable(self, code, f):
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
        ns.fname = self.m._field_name(f)
        ns.ww(
        """
            if {fname} is None:
                {fname}_is_null = 1
                {fname}_value = 0
            else:
                {fname}_is_null = 0
                {fname}_value = {fname}
        """)

    def handle_text(self, code, f):
        fname = self.llname[f]
        code.w('{arg} = builder.alloc_text({offset}, {arg})',
               arg=fname, offset=self.layout.slot_offset(f))

    def handle_data(self, code, f):
        fname = self.llname[f]
        code.w('{arg} = builder.alloc_data({offset}, {arg})',
               arg=fname, offset=self.layout.slot_offset(f))

    def handle_struct(self, code, f):
        fname = self.llname[f]
        offset = self.layout.slot_offset(f)
        structname = f.slot.type.runtime_name(self.m)
        code.w('{arg} = builder.alloc_struct({offset}, {structname}, {arg})',
               arg=fname, offset=offset, structname=structname)

    def handle_list(self, code, f):
        ns = code.new_scope()
        ns.fname = self.llname[f]
        ns.offset = self.layout.slot_offset(f)
        itemtype = f.slot.type.list.elementType
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

    def handle_primitive(self, code, f):
        if f.slot.hadExplicitDefault:
            fname = self.llname[f]
            ns = code.new_scope()
            ns.arg = fname
            ns.default_ = f.slot.defaultValue.as_pyobj()
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
        self.llfields = [] # "low level fields", passed to StructBuilder
        self.llname = {}   # for plain fields is simply f.name, but in case
                           # of groups it's groupname_fieldname
        #
        if tag_offset is not None:
            # add a field to represent the tag
            tag_offset /= 2 # from bytes to multiple of int16
            f = Field.new_slot('__which__', tag_offset, Type.new_int16())
            self.llfields.append(f)
            self.llname[f] = '__which__'

    def add_tree(self, tree):
        for node in tree.allslots():
            self.llfields.append(node.f)
            self.llname[node.f] = node.varname
        self._finish()

    def _finish(self):
        """
        Compute the format string and sort llfields in order of offset
        """
        total_length = (self.data_size + self.ptrs_size)*8
        fmt = ['x'] * total_length

        def set(offset, t):
            fmt[offset] = t
            size = struct.calcsize(t)
            for i in range(offset+1, offset+size):
                fmt[i] = None

        self.llfields.sort(key=lambda f: self.slot_offset(f))
        for f in self.llfields:
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
