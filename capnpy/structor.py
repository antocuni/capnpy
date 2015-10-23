"""
Structor -> struct ctor -> struct construtor :)
"""

import struct
from capnpy.schema import Field, Type

class Structor(object):

    _unsupported = None

    def __init__(self, compiler, name, data_size, ptrs_size, fields,
                 tag_offset=None, tag_value=None):
        self.compiler = compiler
        self.name = name
        self.data_size = data_size
        self.ptrs_size = ptrs_size
        self.tag_offset = tag_offset
        self.tag_value = tag_value
        self.fields = self._get_fields(fields)
        self.argnames = self._get_argnames()
        self.fmt = self._compute_format()

    def _get_fields(self, fields):
        if any([f.is_group() for f in fields]):
            self._unsupported = "Group fields not supported yet"
            return fields
        #
        fields = [f for f in fields if not f.is_void()]
        if self.tag_offset is not None:
            # self.tag_offset is expressed in bytes: as usual,
            # field.slot.offset is expressed in multiples of the field size,
            # which is 2 bytes in this case: thus, we need to use tag_offset/2
            tag_field = Field.new_slot('__which__', self.tag_offset/2, Type.new_int16())
            fields.append(tag_field)
        #
        return fields

    def _get_argnames(self):
        # get the names of all fields, except those which are used as "check
        # condition" for nullable fields
        ignored = set()
        for f in self.fields:
            if f.is_nullable(self.compiler):
                # XXX
                self._unsupported = 'nullable fields'
                return ['*args']
                ignored.add(f.nullable_by)
        #
        return [f.name for f in self.fields if f not in ignored]

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
                self._unsupported = 'Unsupported field type: %s' % f
                return
            set(f.slot.get_offset(self.data_size), f.slot.get_fmt())
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
        self.fields.sort(key=lambda f: f.slot.get_offset(self.data_size))
        buildnames = [f.name for f in self.fields]

        if self.tag_value is not None:
            argnames.remove('__which__')
        if len(argnames) != len(set(argnames)):
            raise ValueError("Duplicate field name(s): %s" % argnames)
        code.w('@staticmethod')
        with code.def_(self.name, argnames):
            code.w('builder = __.StructBuilder({fmt})', fmt=repr(self.fmt))
            if self.tag_value is not None:
                code.w('__which__ = {tag_value}', tag_value=int(self.tag_value))
            for f in self.fields:
                ## if isinstance(f, field.NullablePrimitive):
                ##     self._field_nullable(code, f)
                if f.is_string():
                    self._field_string(code, f)
                elif f.is_struct():
                    self._field_struct(code, f)
                elif f.is_list():
                    self._field_list(code, f)
                elif f.is_primitive():
                    pass # nothing to do
                else:
                    code.w("raise NotImplementedError('Unsupported field type: {f}')",
                           f=str(f))
                #
            code.w('buf =', code.call('builder.build', buildnames))
            code.w('return buf')

    def _field_nullable(self, code, f):
        with code.block('if {arg} is None:', arg=f.name):
            code.w('{isnull} = 1', isnull=f.nullable_by.name)
            code.w('{arg} = 0', arg=f.name)
        with code.block('else:'):
            code.w('{isnull} = 0', isnull=f.nullable_by.name)

    def _field_string(self, code, f):
        code.w('{arg} = builder.alloc_string({offset}, {arg})',
               arg=f.name, offset=f.slot.get_offset(self.data_size))

    def _field_struct(self, code, f):
        offset = f.slot.get_offset(self.data_size)
        structname = self.compiler._get_typename(f.slot.type)
        code.w('{arg} = builder.alloc_struct({offset}, {structname}, {arg})',
               arg=f.name, offset=offset, structname=structname)

    def _field_list(self, code, f):
        offset = f.slot.get_offset(self.data_size)
        item_type = f.slot.type.list.elementType
        item_type_name = self.compiler._get_typename(item_type)
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
               arg=f.name, offset=offset, listcls=listcls, itemtype=item_type_name)
