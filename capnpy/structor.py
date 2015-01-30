"""
Structor -> struct ctor -> struct construtor :)
"""

import struct
from pypytools.codegen import Code
from capnpy import field
from capnpy.type import Types
from capnpy.builder import StructBuilder

class Unsupported(Exception):
    pass

def structor(name, data_size, ptrs_size, fields, tag_offset=None, tag_value=None):
    if field.Group in [type(f) for f in fields]:
        return make_unsupported(name, "Group fields not supported yet")
    #
    fields = [f for f in fields if not isinstance(f, field.Void)]
    if tag_offset is not None:
        tag_field = field.Primitive('__which__', tag_offset, Types.int16)
        fields.append(tag_field)
    fields.sort(key=lambda f: f.offset) # sort the field in offset ascending order
    try:
        fmt = compute_format(data_size, ptrs_size, fields)
        return make_structor(name, fields, fmt, tag_value)
    except Unsupported, e:
        return make_unsupported(name, str(e))

def make_unsupported(name, msg):
    def fn(*args, **kwargs):
        raise NotImplementedError(msg)
    fn.__name__ = name
    return fn

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

def make_structor(name, fields, fmt, tag_value):
    ## create a constructor which looks like this
    ## def ctor(cls, x, y, z):
    ##     builder = StructBuilder('qqq')
    ##     z = builder.alloc_string(16, z)
    ##     buf = builder.build(x, y)
    ##     return cls.from_buffer(buf, 0, None)
    #
    argnames = [f.name for f in fields]
    buildnames = argnames[:]
    if tag_value is not None:
        argnames.remove('__which__')
    if len(argnames) != len(set(argnames)):
        raise ValueError("Duplicate field name(s): %s" % argnames)
    code = Code()
    code['StructBuilder'] = StructBuilder
    with code.def_(name, ['cls'] + argnames):
        code.w('builder = StructBuilder({fmt})', fmt=repr(fmt))
        if tag_value is not None:
            code.w('__which__ = {tag_value}', tag_value=int(tag_value))
        for f, arg in zip(fields, argnames):
            if isinstance(f, field.Primitive):
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
        code.w('return cls.from_buffer(buf, 0, None)')
    code.compile()
    return code[name]
