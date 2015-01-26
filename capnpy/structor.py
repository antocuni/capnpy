"""
Structor -> struct ctor -> struct construtor :)
"""

import struct
from pypytools.unroll import unroll
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
        # PyPy-specific optimization: we want "fmt" to be constant-folded:
        # however, as of PyPy 2.5, the JIT is not able to constant-fold
        # closure variables. The workaround is to put fmt inside a class: the
        # lookup of class attribute is always guarded by an out-of-line guard,
        # so Vars.fmt is correctly seen as a constant by the JIT.
        class Vars(object):
            fmt = self.fmt

        fields = enumerate(self.fields)
        @unroll(fields=fields)
        def call(*args):
            builder = StructBuilder(Vars.fmt)
            newargs = ()
            for i, f in fields:
                arg = args[i]
                if isinstance(f, field.Primitive):
                    newargs += (arg,)
                else:
                    assert False
            return builder.build(*newargs)

        return call

    def __call__(self, *args):
        return self._call(*args)
