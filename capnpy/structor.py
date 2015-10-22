"""
Structor -> struct ctor -> struct construtor :)
"""

import struct
from capnpy import field
from capnpy.type import Types

class Structor(object):

    _unsupported = None

    def __init__(self, name, data_size, ptrs_size, fields,
                 tag_offset=None, tag_value=None):
        self.name = name
        self.data_size = data_size
        self.ptrs_size = ptrs_size
        self.tag_offset = tag_offset
        self.tag_value = tag_value
        self.fields = self._get_fields(fields)
        self.fmt = self._compute_format()

    def _get_fields(self, fields):
        if field.Group in [type(f) for f in fields]:
            self._unsupported = "Group fields not supported yet"
            return
        #
        fields = [f for f in fields if not isinstance(f, field.Void)]
        if self.tag_offset is not None:
            tag_field = field.Primitive('__which__', self.tag_offset, Types.int16)
            fields.append(tag_field)
        #
        return fields

    def _compute_format(self):
        total_length = (self.data_size + self.ptrs_size)*8
        fmt = ['x'] * total_length

        def set(offset, t):
            fmt[offset] = t
            size = struct.calcsize(t)
            for i in range(offset+1, offset+size):
                fmt[i] = None

        for f in self.fields:
            if not hasattr(f, 'fmt'):
                self._unsupported = 'Unsupported field type: %s' % f
                return
            set(f.offset, f.fmt)
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

    def _get_argnames(self):
        # get the names of all fields, except those which are used as "check
        # condition" for nullable fields
        ignored = set()
        for f in self.fields:
            if isinstance(f, field.NullablePrimitive):
                ignored.add(f.nullable_by)
        #
        return [f.name for f in self.fields if f not in ignored]

    def _decl_ctor(self, code):
        ## generate a constructor which looks like this
        ## @staticmethod
        ## def ctor(x, y, z):
        ##     builder = StructBuilder('qqq')
        ##     z = builder.alloc_string(16, z)
        ##     buf = builder.build(x, y)
        ##     return buf
        #
        # the parameters have the same order as fields
        argnames = self._get_argnames()

        # for for building, we sort them by offset
        self.fields.sort(key=lambda f: f.offset)
        buildnames = [f.name for f in self.fields]

        if self.tag_value is not None:
            argnames.remove('__which__')
        if len(argnames) != len(set(argnames)):
            raise ValueError("Duplicate field name(s): %s" % argnames)
        code.w('@staticmethod')
        with code.def_(self.name, argnames):
            code.w('builder = StructBuilder({fmt})', fmt=repr(self.fmt))
            if self.tag_value is not None:
                code.w('__which__ = {tag_value}', tag_value=int(self.tag_value))
            for f in self.fields:
                arg = f.name
                if isinstance(f, field.NullablePrimitive):
                    with code.block('if {arg} is None:', arg=arg):
                        code.w('{isnull} = 1', isnull=f.nullable_by.name)
                        code.w('{arg} = 0', arg=arg)
                    with code.block('else:'):
                        code.w('{isnull} = 0', isnull=f.nullable_by.name)
                elif isinstance(f, field.Primitive):
                    pass # nothing to do
                elif isinstance(f, field.String):
                    code.w('{arg} = builder.alloc_string({offset}, {arg})',
                           arg=arg, offset=f.offset)
                elif isinstance(f, field.Struct):
                    structname = code.new_global(f.structcls.__name__, f.structcls)
                    code.w('{arg} = builder.alloc_struct({offset}, {structname}, {arg})',
                           arg=arg, offset=f.offset, structname=structname)
                elif isinstance(f, field.List):
                    listcls = code.new_global(f.listcls.__name__, f.listcls)
                    itemtype = code.new_global('item_type', f.item_type)
                    code.w('{arg} = builder.alloc_list({offset}, {listcls}, {itemtype}, {arg})',
                           arg=arg, offset=f.offset, listcls=listcls, itemtype=itemtype)
                else:
                    raise NotImplementedError('Unsupported field type: %s' % f)
                #
            code.w('buf =', code.call('builder.build', buildnames))
            code.w('return buf')

