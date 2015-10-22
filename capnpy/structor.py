"""
Structor -> struct ctor -> struct construtor :)
"""

import struct
from capnpy import field
from capnpy.type import Types

class Unsupported(Exception):
    pass

def define_structor(code, name, data_size, ptrs_size, fields,
                    tag_offset=None, tag_value=None):
    if field.Group in [type(f) for f in fields]:
        return make_unsupported(name, "Group fields not supported yet")
    #
    fields = [f for f in fields if not isinstance(f, field.Void)]
    if tag_offset is not None:
        tag_field = field.Primitive('__which__', tag_offset, Types.int16)
        fields.append(tag_field)
    try:
        fmt = compute_format(data_size, ptrs_size, fields)
        return make_structor(code, name, fields, fmt, tag_value)
    except Unsupported, e:
        return make_unsupported(code, name, str(e))

def make_unsupported(code, name, msg):
    code.w('@staticmethod')
    with code.def_(name, ['*args', '**kwargs']):
        code.w('raise NotImplementedError({msg})', msg=repr(msg))

def compute_format(data_size, ptrs_size, fields):
    total_length = (data_size+ptrs_size)*8
    fmt = ['x'] * total_length

    def set(offset, t):
        fmt[offset] = t
        size = struct.calcsize(t)
        for i in range(offset+1, offset+size):
            fmt[i] = None

    for f in fields:
        if not hasattr(f, 'fmt'):
            raise Unsupported('Unsupported field type: %s' % f)
        set(f.offset, f.fmt)
    #
    # remove all the Nones
    fmt = [ch for ch in fmt if ch is not None]
    fmt = ''.join(fmt)
    assert struct.calcsize(fmt) == total_length
    return fmt

def get_argnames(fields):
    # get the names of all fields, except those which are used as "check
    # condition" for nullable fields
    ignored = set()
    for f in fields:
        if isinstance(f, field.NullablePrimitive):
            ignored.add(f.nullable_by)
    #
    return [f.name for f in fields if f not in ignored]

def make_structor(code, name, fields, fmt, tag_value):
    ## generate a constructor which looks like this
    ## @staticmethod
    ## def ctor(x, y, z):
    ##     builder = StructBuilder('qqq')
    ##     z = builder.alloc_string(16, z)
    ##     buf = builder.build(x, y)
    ##     return buf
    #
    # the parameters have the same order as fields
    argnames = get_argnames(fields)

    # for for building, we sort them by offset
    fields.sort(key=lambda f: f.offset)
    buildnames = [f.name for f in fields]
    
    if tag_value is not None:
        argnames.remove('__which__')
    if len(argnames) != len(set(argnames)):
        raise ValueError("Duplicate field name(s): %s" % argnames)
    code.w('@staticmethod')
    with code.def_(name, argnames):
        code.w('builder = StructBuilder({fmt})', fmt=repr(fmt))
        if tag_value is not None:
            code.w('__which__ = {tag_value}', tag_value=int(tag_value))
        for f in fields:
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
                raise Unsupported('Unsupported field type: %s' % f)
            #
        code.w('buf =', code.call('builder.build', buildnames))
        code.w('return buf')
