import struct

cpdef unpack_primitive(char* sfmt, bytes buf, int offset):
    cdef char* cbuf
    cdef void* valueaddr
    cdef long value
    cdef char fmt = sfmt[0]
    #
    cbuf = buf
    valueaddr = cbuf + offset
    if fmt == 'q':
        return (<long*>valueaddr)[0]
    elif fmt == 'Q':
        # XXX: this return a Python long: fix it to return a long only if
        # strictly necessary
        return (<unsigned long*>valueaddr)[0]
    #
    # slow fallback
    return struct.unpack_from('<' + sfmt, buf, offset)[0]
    #raise ValueError('unknown fmt %s' % chr(fmt))
