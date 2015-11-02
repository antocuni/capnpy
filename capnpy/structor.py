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
        self.nullable_by = {} # field -> NullableGroup
        #
        try:
            self.init_fields(fields)
            self.fmt = self._compute_format()
        except Unsupported as e:
            self.argnames = ['*args']
            self._unsupported = e.message

    def init_fields(self, fields):
        for f in fields:
            ngroup = f.is_nullable(self.m)
            if ngroup:
                # add isNull and value to fields, but use the group name in the arguments
                self._append_field(ngroup.is_null, ngroup.name)
                self._append_field(ngroup.value, ngroup.name)
                self.argnames.append(ngroup.name)
                self.nullable_by[ngroup.value] = ngroup
            elif f.is_group():
                raise Unsupported("Group fields not supported yet")
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

    def _append_field(self, f, prefix=None):
        name = f.name
        if prefix:
            name = '%s_%s' % (prefix, name)
        self.fields.append(f)
        self.field_name[f] = name
        return name

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
                raise Unsupported('Unsupported field type: %s' % f)
            set(f.slot.compute_offset_inside(self.data_size), f.slot.get_fmt())
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
        with code.def_(self.name, ['*args', '**kwargs']):
            code.w('raise NotImplementedError({msg})', msg=repr(self._unsupported))

    def _decl_ctor(self, code):
        ## generate a constructor which looks like this
        ## @staticmethod
        ## def ctor(x, y, z):
        ##     builder = __.StructBuilder('qqq')
        ##     z = builder.alloc_string(16, z)
        ##     buf = builder.build(x, y)
        ##     return buf
        #
        # the parameters have the same order as fields
        argnames = self.argnames

        # for for building, we sort them by offset
        self.fields.sort(key=lambda f: f.slot.compute_offset_inside(self.data_size))
        buildnames = [self.field_name[f] for f in self.fields]

        if len(argnames) != len(set(argnames)):
            raise ValueError("Duplicate field name(s): %s" % argnames)
        code.w('@staticmethod')
        with code.def_(self.name, argnames):
            code.w('builder = __.StructBuilder({fmt})', fmt=repr(self.fmt))
            if self.tag_value is not None:
                code.w('__which__ = {tag_value}', tag_value=int(self.tag_value))
            for f in self.fields:
                if f.is_string():
                    self._field_string(code, f)
                elif f.is_struct():
                    self._field_struct(code, f)
                elif f.is_list():
                    self._field_list(code, f)
                elif f in self.nullable_by:
                    self._field_nullable(code, f)
                elif f.is_primitive():
                    pass # nothing to do
                else:
                    code.w("raise NotImplementedError('Unsupported field type: {f}')",
                           f=str(f))
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
        ngroup = self.nullable_by[f]
        is_null = self.field_name[ngroup.is_null]
        value = self.field_name[ngroup.value]
        with code.block('if {arg} is None:', arg=ngroup.name):
            code.w('{is_null} = 1', is_null=is_null)
            code.w('{value} = 0', value=value)
        with code.block('else:'):
            code.w('{is_null} = 0', is_null=is_null)
            code.w('{value} = {arg}', value=value, arg=ngroup.name)

    def _field_string(self, code, f):
        fname = self.field_name[f]
        code.w('{arg} = builder.alloc_string({offset}, {arg})',
               arg=fname, offset=f.slot.compute_offset_inside(self.data_size))

    def _field_struct(self, code, f):
        fname = self.field_name[f]
        offset = f.slot.compute_offset_inside(self.data_size)
        structname = self.m._get_typename(f.slot.type)
        code.w('{arg} = builder.alloc_struct({offset}, {structname}, {arg})',
               arg=fname, offset=offset, structname=structname)

    def _field_list(self, code, f):
        fname = self.field_name[f]
        offset = f.slot.compute_offset_inside(self.data_size)
        item_type = f.slot.type.list.elementType
        item_type_name = self.m._get_typename(item_type)
        #
        if item_type.is_primitive():
            listcls = '__.PrimitiveList'
        elif item_type.is_string():
            listcls = '__.StringList'
        elif item_type.is_struct():
            listcls = '__.StructList'
        else:
            raise ValueError('Unknown item type: %s' % item_type)
        #
        code.w('{arg} = builder.alloc_list({offset}, {listcls}, {itemtype}, {arg})',
               arg=fname, offset=offset, listcls=listcls, itemtype=item_type_name)
