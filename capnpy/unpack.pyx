import struct

cdef checkbound(int size, bytes buf, int offset):
    if offset + size > len(buf):
        raise IndexError('Offset out of bounds: %d' % offset)

cpdef unpack_primitive(char ifmt, bytes buf, int offset):
    cdef char* cbuf
    cdef void* valueaddr
    cdef long value
    #
    if offset < 0:
        raise IndexError('Offset out of bounds: %d' % offset)
    cbuf = buf
    valueaddr = cbuf + offset
    if ifmt == 'q':
        checkbound(8, buf, offset)
        return (<long*>valueaddr)[0]
    elif ifmt == 'Q':
        checkbound(8, buf, offset)
        # XXX: this return a Python long: fix it to return a long only if
        # strictly necessary
        return (<unsigned long*>valueaddr)[0]
    #
    # slow fallback
    return struct.unpack_from('<' + chr(ifmt), buf, offset)[0]
    #raise ValueError('unknown fmt %s' % chr(ifmt))


