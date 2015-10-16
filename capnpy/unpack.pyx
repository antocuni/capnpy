import struct

# unpack_primitive is the only official API exported by this module, and it's
# implemented also by the pure-python unpack.py which is used by PyPy.
#
# __unpack_primitive_fast is for internal usage only, and it's called by
# cython's based automatically generated schema files; it doesn't exist in the
# pure Python module, and should not be called by user's code. It is needed to
# avoid the cost of converting fmt chars like 'q' into a string and back to
# char again.

cpdef unpack_primitive(char* sfmt, bytes buf, int offset):
    return __unpack_primitive_fast(sfmt[0], buf, offset)

cpdef __unpack_primitive_fast(char fmt, bytes buf, int offset):
    cdef char* cbuf
    cdef void* valueaddr
    cdef long value
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
    return struct.unpack_from('<' + fmt, buf, offset)[0]
    #raise ValueError('unknown fmt %s' % chr(fmt))


