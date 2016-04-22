import struct
from pypytools import IS_PYPY

if IS_PYPY:
    # workaround for a limitation of the PyPy JIT: struct.unpack is optimized
    # only if the format string is a tracing-time constant; this is because of
    # this line in rlib/rstruct/formatiterator.py:
    #    @jit.look_inside_iff(lambda self, fmt: jit.isconstant(fmt))
    #    def interpret(self, fmt):
    #        ...
    #
    # The problem is that if you use struct.unpack(chr(113), '...'), chr(113)
    # is not a tracing-time constant (it becomes constant later, during
    # optimizeopt). The work around is to use mychr, which pyjitpl.py is smart
    # enough to detect as a tracing-time constant.
    _CHR = tuple(map(chr, range(256)))
    def mychr(i):
        return _CHR[i]

else:
    mychr = chr

def unpack_primitive(ifmt, buf, offset):
    fmt = '<' + mychr(ifmt)
    if offset < 0 or offset + struct.calcsize(fmt) > len(buf):
        raise IndexError('Offset out of bounds: %d' % offset)
    return struct.unpack_from(fmt, buf, offset)[0]

def unpack_int64(buf, offset):
    return unpack_primitive(ord('q'), buf, offset)

def unpack_int16(buf, offset):
    return unpack_primitive(ord('h'), buf, offset)

def unpack_uint32(buf, offset):
    return unpack_primitive(ord('I'), buf, offset)
