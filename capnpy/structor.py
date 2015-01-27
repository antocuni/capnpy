"""
Structor -> struct ctor -> struct construtor :)
"""

import struct
from pypytools.codegen import Code
from capnpy import field
from capnpy.builder import StructBuilder

class Structor(object):

    def __init__(self, data_size, ptrs_size, fields):
        self.data_size = data_size
        self.ptrs_size = ptrs_size
        self.fields = fields
        self.fmt = self.compute_format()
        self._call = self.make_call()

    def compute_format(self):
        total_length = (self.data_size+self.ptrs_size)*8
        fmt = ['x'] * total_length
        for f in self.fields:
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

    def make_call(self):
        argnames = ['arg%d' % i for i in range(len(self.fields))]
        code = Code()
        code['StructBuilder'] = StructBuilder
        with code.def_('call', argnames):
            code.w('builder = StructBuilder({fmt})', fmt=repr(self.fmt))
            code.w('return', code.call('builder.build', argnames))
        code.compile()
        return code['call']


    def __call__(self, *args):
        return self._call(*args)
