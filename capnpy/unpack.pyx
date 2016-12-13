from libc.stdint cimport (int8_t, uint8_t, int16_t, uint16_t,
                          uint32_t, int32_t, int64_t, uint64_t, INT64_MAX)
from cpython.string cimport PyString_GET_SIZE, PyString_AS_STRING, PyString_Check

cdef char* as_cbuf(object buf):
    # PyString_AS_STRING seems to be faster than relying of cython's own logic
    # to convert bytes to char*
    cdef bytes bytes_buf
    if PyString_Check(buf):
        bytes_buf = buf
        return PyString_AS_STRING(bytes_buf)
    else:
        return buf

cdef checkbound(int size, object buf, int offset):
    cdef Py_ssize_t length = 0
    if PyString_Check(buf):
        length = PyString_GET_SIZE(buf)
    else:
        length = len(buf)
    if offset + size > length:
        raise IndexError('Offset out of bounds: %d' % offset)

cpdef unpack_primitive(char ifmt, object buf, int offset):
    cdef char* cbuf
    cdef void* valueaddr
    cdef uint64_t uint64_value
    #
    if offset < 0:
        raise IndexError('Offset out of bounds: %d' % offset)
    cbuf = as_cbuf(buf)
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


cpdef long unpack_int64(object buf, int offset):
    cdef char* cbuf
    cdef void* valueaddr
    #
    if offset < 0:
        raise IndexError('Offset out of bounds: %d' % offset)
    cbuf = as_cbuf(buf)
    valueaddr = cbuf + offset
    checkbound(8, buf, offset)
    return (<int64_t*>valueaddr)[0]

cpdef long unpack_int16(object buf, int offset):
    cdef char* cbuf
    cdef void* valueaddr
    #
    if offset < 0:
        raise IndexError('Offset out of bounds: %d' % offset)
    cbuf = as_cbuf(buf)
    valueaddr = cbuf + offset
    checkbound(2, buf, offset)
    return (<int16_t*>valueaddr)[0]

cpdef long unpack_uint32(object buf, int offset):
    cdef char* cbuf
    cdef void* valueaddr
    #
    if offset < 0:
        raise IndexError('Offset out of bounds: %d' % offset)
    cbuf = as_cbuf(buf)
    valueaddr = cbuf + offset
    checkbound(4, buf, offset)
    return (<uint32_t*>valueaddr)[0]
