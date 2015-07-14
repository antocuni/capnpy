import struct

cpdef unpack_primitive(char* sfmt, bytes buf, int offset):
    cdef char* cbuf
    cdef void* valueaddr
    cdef long value
    cdef char fmt = sfmt[0]
    if fmt == 'q':
        cbuf = buf
        valueaddr = cbuf + offset
        value = (<long*>valueaddr)[0]
        return value
    return struct.unpack_from('<' + sfmt, buf, offset)[0]
    #raise ValueError('unknown fmt %s' % chr(fmt))
