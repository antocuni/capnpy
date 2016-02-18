from libc.stdint cimport (int8_t, uint8_t, int16_t, uint16_t,
                          uint32_t, int32_t, int64_t, uint64_t)

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
        return (<int64_t*>valueaddr)[0]
    elif ifmt == 'Q':
        checkbound(8, buf, offset)
        # XXX: this return a Python long: fix it to return a long only if
        # strictly necessary
        return (<uint64_t*>valueaddr)[0]
    elif ifmt == 'd':
        checkbound(8, buf, offset)
        return (<double*>valueaddr)[0]
    elif ifmt == 'f':
        checkbound(8, buf, offset)
        return (<float*>valueaddr)[0]
    elif ifmt == 'i':
        checkbound(4, buf, offset)
        return (<int32_t*>valueaddr)[0]
    elif ifmt == 'I':
        checkbound(4, buf, offset)
        return (<uint32_t*>valueaddr)[0]
    elif ifmt == 'h':
        checkbound(2, buf, offset)
        return (<int16_t*>valueaddr)[0]
    elif ifmt == 'H':
        checkbound(2, buf, offset)
        return (<uint16_t*>valueaddr)[0]
    elif ifmt == 'b':
        checkbound(1, buf, offset)
        return (<int8_t*>valueaddr)[0]
    elif ifmt == 'B':
        checkbound(1, buf, offset)
        return (<uint8_t*>valueaddr)[0]
    #
    raise ValueError('unknown fmt %s' % chr(ifmt))


