from libc.stdint cimport (int8_t, uint8_t, int16_t, uint16_t,
                          uint32_t, int32_t, int64_t, uint64_t, INT64_MAX)
from cpython.string cimport (PyString_GET_SIZE, PyString_AS_STRING,
                             PyString_CheckExact, PyString_FromStringAndSize)

mychr = chr

cdef extern from "Python.h":
    int PyByteArray_CheckExact(object o)
    char* PyByteArray_AS_STRING(object o)
    Py_ssize_t PyByteArray_GET_SIZE(object o)

cdef char* as_cbuf(object buf, Py_ssize_t* length, bint rw=0) except NULL:
    # PyString_AS_STRING seems to be faster than relying of cython's own logic
    # to convert bytes to char*
    cdef bytes bytes_buf
    cdef bytearray ba_buf
    if not rw and PyString_CheckExact(buf):
        bytes_buf = buf
        length[0] = PyString_GET_SIZE(bytes_buf)
        return PyString_AS_STRING(bytes_buf)
    elif PyByteArray_CheckExact(buf):
        ba_buf = buf
        length[0] = PyByteArray_GET_SIZE(ba_buf)
        return PyByteArray_AS_STRING(ba_buf)
    else:
        if rw:
            raise TypeError("Expected bytearray")
        else:
            raise TypeError("Expected str or bytearray")

cdef checkbound(int size, Py_ssize_t length, int offset):
    if offset < 0 or offset + size > length:
        raise IndexError('Offset out of bounds: %d' % offset)

cpdef unpack_primitive(char ifmt, object buf, int offset):
    cdef char* cbuf
    cdef void* valueaddr
    cdef uint64_t uint64_value
    cdef Py_ssize_t length = 0
    cbuf = as_cbuf(buf, &length)
    valueaddr = cbuf + offset
    if ifmt == 'q':
        checkbound(8, length, offset)
        return (<int64_t*>valueaddr)[0]
    elif ifmt == 'Q':
        # if the value is small enough, it returns a python int. Else, a
        # python long
        checkbound(8, length, offset)
        uint64_value = (<uint64_t*>valueaddr)[0]
        if uint64_value <= INT64_MAX:
            return <int64_t>uint64_value
        else:
            return uint64_value
    elif ifmt == 'd':
        checkbound(8, length, offset)
        return (<double*>valueaddr)[0]
    elif ifmt == 'f':
        checkbound(4, length, offset)
        return (<float*>valueaddr)[0]
    elif ifmt == 'i':
        checkbound(4, length, offset)
        return (<int32_t*>valueaddr)[0]
    elif ifmt == 'I':
        checkbound(4, length, offset)
        return (<uint32_t*>valueaddr)[0]
    elif ifmt == 'h':
        checkbound(2, length, offset)
        return (<int16_t*>valueaddr)[0]
    elif ifmt == 'H':
        checkbound(2, length, offset)
        return (<uint16_t*>valueaddr)[0]
    elif ifmt == 'b':
        checkbound(1, length, offset)
        return (<int8_t*>valueaddr)[0]
    elif ifmt == 'B':
        checkbound(1, length, offset)
        return (<uint8_t*>valueaddr)[0]
    #
    raise ValueError('unknown fmt %s' % chr(ifmt))


cpdef long unpack_int64(object buf, int offset):
    cdef char* cbuf
    cdef void* valueaddr
    cdef Py_ssize_t length = 0
    cbuf = as_cbuf(buf, &length)
    valueaddr = cbuf + offset
    checkbound(8, length, offset)
    return (<int64_t*>valueaddr)[0]

cpdef long unpack_int16(object buf, int offset):
    cdef char* cbuf
    cdef void* valueaddr
    cdef Py_ssize_t length = 0
    cbuf = as_cbuf(buf, &length)
    valueaddr = cbuf + offset
    checkbound(2, length, offset)
    return (<int16_t*>valueaddr)[0]

cpdef long unpack_uint32(object buf, int offset):
    cdef char* cbuf
    cdef void* valueaddr
    cdef Py_ssize_t length = 0
    cbuf = as_cbuf(buf, &length)
    valueaddr = cbuf + offset
    checkbound(4, length, offset)
    return (<uint32_t*>valueaddr)[0]

cpdef bytes pack_message_header(int segment_count, int segment_size, long p):
    cdef bytes buf
    cdef char* cbuf
    assert segment_count == 1
    buf = PyString_FromStringAndSize(NULL, 16)
    cbuf = PyString_AS_STRING(buf)
    (<int32_t*>(cbuf+0))[0] = segment_count-1
    (<int32_t*>(cbuf+4))[0] = segment_size
    (<int64_t*>(cbuf+8))[0] = p
    return buf


cpdef bytes pack_int64(long value):
    cdef bytes buf
    cdef char* cbuf
    buf = PyString_FromStringAndSize(NULL, 8)
    cbuf = PyString_AS_STRING(buf)
    (<int64_t*>(cbuf+0))[0] = value
    return buf

cpdef object pack_into(char ifmt, object buf, int offset, object value):
    cdef char* cbuf
    cdef void* valueaddr
    cdef Py_ssize_t length = 0
    cbuf = as_cbuf(buf, &length, rw=1)
    valueaddr = cbuf + offset
    if ifmt == 'q':
        checkbound(8, length, offset)
        (<int64_t*>valueaddr)[0] = value
    elif ifmt == 'Q':
        checkbound(8, length, offset)
        (<uint64_t*>valueaddr)[0] = value
    elif ifmt == 'd':
        checkbound(8, length, offset)
        (<double*>valueaddr)[0] = value
    elif ifmt == 'f':
        checkbound(4, length, offset)
        (<float*>valueaddr)[0] = value
    elif ifmt == 'i':
        checkbound(4, length, offset)
        (<int32_t*>valueaddr)[0] = value
    elif ifmt == 'I':
        checkbound(4, length, offset)
        (<uint32_t*>valueaddr)[0] = value
    elif ifmt == 'h':
        checkbound(2, length, offset)
        (<int16_t*>valueaddr)[0] = value
    elif ifmt == 'H':
        checkbound(2, length, offset)
        (<uint16_t*>valueaddr)[0] = value
    elif ifmt == 'b':
        checkbound(1, length, offset)
        (<int8_t*>valueaddr)[0] = value
    elif ifmt == 'B':
        checkbound(1, length, offset)
        (<uint8_t*>valueaddr)[0] = value
    else:
        raise ValueError('unknown fmt %s' % chr(ifmt))
    return None

cpdef object pack_int64_into(object buf, int offset, long value):
    cdef char* cbuf
    cdef void* valueaddr
    cdef Py_ssize_t length = 0
    cbuf = as_cbuf(buf, &length, rw=1)
    valueaddr = cbuf + offset
    checkbound(8, length, offset)
    (<int64_t*>valueaddr)[0] = value
