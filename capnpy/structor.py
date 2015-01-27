"""
Structor -> struct ctor -> struct construtor :)
"""

import struct
from pypytools.codegen import Code
from capnpy import field
from capnpy.builder import StructBuilder

def structor(name, data_size, ptrs_size, fields):
    fields = [f for f in fields if not isinstance(f, field.Void)]
    fmt = compute_format(data_size, ptrs_size, fields)
    return make_structor(name, fields, fmt)

def compute_format(data_size, ptrs_size, fields):
    total_length = (data_size+ptrs_size)*8
    fmt = ['x'] * total_length

    def set(offset, t):
        fmt[offset] = t
        size = struct.calcsize(t)
        for i in range(offset+1, offset+size):
            fmt[i] = None

    for f in fields:
        if isinstance(f, field.Primitive):
            set(f.offset, f.type.fmt)
        elif isinstance(f, (field.String, field.Struct)):
            set(f.offset, 'q')
        else:
            assert False
    #
    # remove all the Nones
    fmt = [ch for ch in fmt if ch is not None]
    fmt = ''.join(fmt)
    assert struct.calcsize(fmt) == total_length
    return fmt

def make_structor(name, fields, fmt):
    argnames = ['arg%d' % i for i in range(len(fields))]
    code = Code()
    code['StructBuilder'] = StructBuilder
    with code.def_(name, ['cls'] + argnames):
        code.w('builder = StructBuilder({fmt})', fmt=repr(fmt))
        for f, arg in zip(fields, argnames):
            if isinstance(f, field.String):
                code.w('{arg} = builder.alloc_string({offset}, {arg})',
                       arg=arg, offset=f.offset)
            elif isinstance(f, field.Struct):
                structname = f.structcls.__name__
                code.w('{arg} = builder.alloc_struct({offset}, {structname}, {arg})',
                       arg=arg, offset=f.offset, structname=structname)
                code[structname] = f.structcls
            else:
                assert isinstance(f, field.Primitive)
            #
        code.w('buf =', code.call('builder.build', argnames))
        code.w('return cls.from_buffer(buf, 0, None)')
    code.compile()
    return code[name]
