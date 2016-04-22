from libc.stdint cimport (int8_t, uint8_t, int16_t, uint16_t,
                          uint32_t, int32_t, int64_t, uint64_t, INT64_MAX)

cdef checkbound(int size, bytes buf, int offset):
    if offset + size > len(buf):
        raise IndexError('Offset out of bounds: %d' % offset)

cpdef unpack_primitive(char ifmt, bytes buf, int offset):
    cdef char* cbuf
    cdef void* valueaddr
    cdef uint64_t uint64_value
    #
    if offset < 0:
        raise IndexError('Offset out of bounds: %d' % offset)
    cbuf = buf
    valueaddr = cbuf + offset
    if ifmt == 'q':
        checkbound(8, buf, offset)
        return (<int64_t*>valueaddr)[0]
    elif ifmt == 'Q':
        # if the value is small enough, it returns a python int. Else, a
        # python long
        checkbound(8, buf, offset)
        uint64_value = (<uint64_t*>valueaddr)[0]
        if uint64_value <= INT64_MAX:
            return <int64_t>uint64_value
        else:
            return uint64_value
    elif ifmt == 'd':
        checkbound(8, buf, offset)
        return (<double*>valueaddr)[0]
    elif ifmt == 'f':
        checkbound(4, buf, offset)
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


cpdef long unpack_int64(bytes buf, int offset):
    cdef char* cbuf
    cdef void* valueaddr
    #
    if offset < 0:
        raise IndexError('Offset out of bounds: %d' % offset)
    cbuf = buf
    valueaddr = cbuf + offset
    checkbound(8, buf, offset)
    return (<int64_t*>valueaddr)[0]

cpdef long unpack_int16(bytes buf, int offset):
    cdef char* cbuf
    cdef void* valueaddr
    #
    if offset < 0:
        raise IndexError('Offset out of bounds: %d' % offset)
    cbuf = buf
    valueaddr = cbuf + offset
    checkbound(2, buf, offset)
    return (<int16_t*>valueaddr)[0]

cpdef long unpack_uint32(bytes buf, int offset):
    cdef char* cbuf
    cdef void* valueaddr
    #
    if offset < 0:
        raise IndexError('Offset out of bounds: %d' % offset)
    cbuf = buf
    valueaddr = cbuf + offset
    checkbound(4, buf, offset)
    return (<uint32_t*>valueaddr)[0]
