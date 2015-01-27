"""
Structor -> struct ctor -> struct construtor :)
"""

import struct
from pypytools.codegen import Code
from capnpy import field
from capnpy.builder import StructBuilder

def structor(name, data_size, ptrs_size, fields):
    fmt = compute_format(data_size, ptrs_size, fields)
    return make_structor(name, fields, fmt)

def compute_format(data_size, ptrs_size, fields):
    total_length = (data_size+ptrs_size)*8
    fmt = ['x'] * total_length
    for f in fields:
        if isinstance(f, field.Primitive):
            fmt[f.offset] = f.type.fmt
            for i in range(f.offset+1, f.offset+f.type.calcsize()):
                fmt[i] = None
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
        code.w('buf =', code.call('builder.build', argnames))
        code.w('return cls.from_buffer(buf, 0, None)')
    code.compile()
    return code[name]
