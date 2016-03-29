"""
Structor -> struct ctor -> struct construtor :)
"""

import struct
from capnpy.schema import Field, Type

class Unsupported(Exception):
    pass

class Structor(object):

    _unsupported = None

    def __init__(self, m, name, data_size, ptrs_size, fields,
                 tag_offset=None, tag_value=None):
        self.m = m
        self.name = name
        self.data_size = data_size
        self.ptrs_size = ptrs_size
        self.tag_offset = tag_offset
        self.tag_value = tag_value
        #
        self.argnames = []    # the arguments accepted by the ctor, in order
        self.fields = []      # the fields as passed to StructBuilder
        self.field_name = {}  # for plain fields is simply f.name, but in case
                              # of groups it's groupname_fieldname
        self.groups = []
        try:
            self.init_fields(fields)
            self.fmt = self._compute_format()
        except Unsupported as e:
            self.argnames = ['*args']
            self._unsupported = e.message

    def init_fields(self, fields):
        for f in fields:
            if f.is_nullable(self.m):
                # use "foo_is_null" and "foo_value" as fields, but "foo" in the arguments
                fname, f_is_null, f_value = self._unpack_nullable(f)
                self._append_field(f_is_null, fname)
                self._append_field(f_value, fname)
                self.argnames.append(fname)
                f_value.nullable_group = fname
            elif f.is_group():
                fname = self._append_group(f)
                self.argnames.append(fname)
            elif f.is_void():
                continue # ignore void fields
            else:
                fname = self._append_field(f)
                self.argnames.append(fname)

        if self.tag_offset is not None:
            # add a field to represent the tag, but don't add it to argnames,
            # as it's implicit
            tag_offset = self.tag_offset/2 # from bytes to multiple of int16
            tag_field = Field.new_slot('__which__', tag_offset, Type.new_int16())
            self._append_field(tag_field)

    def _unpack_nullable(self, field):
        assert field.is_group()
        name = self.m._field_name(field)
        def error():
            msg = '%s: nullable groups must have exactly two fields: "isNull" and "value"'
            raise ValueError(msg % name)
        #
        group = self.m.allnodes[field.group.typeId]
        if len(group.struct.fields) != 2:
            error()
        f_is_null, f_value = group.struct.fields
        if f_is_null.name != 'isNull':
            error()
        if f_value.name != 'value':
            error()
        return name, f_is_null, f_value

    def _append_field(self, f, prefix=None):
        name = self.m._field_name(f)
        if prefix:
            name = '%s_%s' % (prefix, name)
        self.fields.append(f)
        self.field_name[f] = name
        return name

    def _append_group(self, f):
        groupname = self.m._field_name(f)
        group = self.m.allnodes[f.group.typeId]
        self.groups.append((groupname, group))
        for i, f in enumerate(group.struct.fields):
            if f.is_void():
                continue
            self.fields.append(f)
            self.field_name[f] = '%s_%d' % (groupname, i)
        return groupname

    def _slot_offset(self, f):
        offset = f.slot.offset * f.slot.get_size()
        if f.slot.type.is_pointer():
            offset += self.data_size*8
        return offset

    def _compute_format(self):
        total_length = (self.data_size + self.ptrs_size)*8
        fmt = ['x'] * total_length

        def set(offset, t):
            fmt[offset] = t
            size = struct.calcsize(t)
            for i in range(offset+1, offset+size):
                fmt[i] = None

        for f in self.fields:
            if not f.is_slot() or f.slot.type.is_bool():
                raise Unsupported('Unsupported field type: %s' % f.shortrepr())
            set(self._slot_offset(f), f.slot.get_fmt())
        #
        # remove all the Nones
        fmt = [ch for ch in fmt if ch is not None]
        fmt = ''.join(fmt)
        assert struct.calcsize(fmt) == total_length
        return fmt

    def declare(self, code):
        if self._unsupported is not None:
            return self._decl_unsupported(code)
        else:
            return self._decl_ctor(code)

    def _decl_unsupported(self, code):
        code.w('@staticmethod')
        with code.def_(self.name, self.m.robust_arglist(self.argnames)):
            code.w('raise NotImplementedError({msg})', msg=repr(self._unsupported))

    def _decl_ctor(self, code):
        ## generate a constructor which looks like this
        ## @staticmethod
        ## def ctor(x, y, z):
        ##     builder = _StructBuilder('qqq')
        ##     z = builder.alloc_text(16, z)
        ##     buf = builder.build(x, y)
        ##     return buf
        #
        # the parameters have the same order as fields
        argnames = self.argnames

        # for for building, we sort them by offset
        self.fields.sort(key=lambda f: self._slot_offset(f))
        buildnames = [self.field_name[f] for f in self.fields]

        if len(argnames) != len(set(argnames)):
            raise ValueError("Duplicate field name(s): %s" % argnames)
        code.w('@staticmethod')
        with code.def_(self.name, self.m.robust_arglist(argnames)):
            code.w('builder = _StructBuilder({fmt})', fmt=repr(self.fmt))
            if self.tag_value is not None:
                code.w('__which__ = {tag_value}', tag_value=int(self.tag_value))
            #
            for groupname, group in self.groups:
                argnames = [self.field_name[f] for f in group.struct.fields
                            if not f.is_void()]
                code.w('{args}, = {groupname}',
                       args=code.args(argnames), groupname=groupname)
            #
            for f in self.fields:
                if f.is_text():
                    self._field_text(code, f)
                elif f.is_data():
                    self._field_data(code, f)
                elif f.is_struct():
                    self._field_struct(code, f)
                elif f.is_list():
                    self._field_list(code, f)
                elif hasattr(f, 'nullable_group'):
                    self._field_nullable(code, f)
                elif f.is_primitive() or f.is_enum():
                    pass # nothing to do
                else:
                    code.w("raise NotImplementedError('Unsupported field type: {f}')",
                           f=f.shortrepr())
                #
            code.w('buf =', code.call('builder.build', buildnames))
            code.w('return buf')

    def _field_nullable(self, code, f):
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
        ns.fname = f.nullable_group
        ns.ww("""
            if {fname} is None:
                {fname}_is_null = 1
                {fname}_value = 0
            else:
                {fname}_is_null = 0
                {fname}_value = {fname}
        """)

    def _field_text(self, code, f):
        fname = self.field_name[f]
        code.w('{arg} = builder.alloc_text({offset}, {arg})',
               arg=fname, offset=self._slot_offset(f))

    def _field_data(self, code, f):
        fname = self.field_name[f]
        code.w('{arg} = builder.alloc_data({offset}, {arg})',
               arg=fname, offset=self._slot_offset(f))

    def _field_struct(self, code, f):
        fname = self.field_name[f]
        offset = self._slot_offset(f)
        structname = f.slot.type.runtime_name(self.m)
        code.w('{arg} = builder.alloc_struct({offset}, {structname}, {arg})',
               arg=fname, offset=offset, structname=structname)

    def _field_list(self, code, f):
        ns = code.new_scope()
        ns.fname = self.field_name[f]
        ns.offset = self._slot_offset(f)
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
