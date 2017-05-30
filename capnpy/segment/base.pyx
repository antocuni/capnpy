cimport cython
from libc.string cimport memcpy
from libc.stdint cimport (int8_t, uint8_t, int16_t, uint16_t,
                          uint32_t, int32_t, int64_t, uint64_t, INT64_MAX)
from cpython.string cimport (PyString_AS_STRING, PyString_GET_SIZE,
                             PyString_FromStringAndSize)

from capnpy cimport ptr

cpdef uint32_t unpack_uint32(bytes buf, Py_ssize_t offset) except? 0xffffffff:
    cdef const char *cbuf = PyString_AS_STRING(buf)
    cdef Py_ssize_t buflen = PyString_GET_SIZE(buf)
    if offset < 0 or offset + 4 > buflen:
        raise IndexError('Offset out of bounds: %d' % (offset+4))
    return (<uint32_t*>(cbuf+offset))[0]


cdef class BaseSegment(object):

    # bah, we need to specify segment_offsets also here, even if it's used
    # only by MultiSegment
    def __cinit__(self, bytes buf, object segment_offsets=None):
        assert buf is not None
        self.buf = buf
        self.cbuf = PyString_AS_STRING(self.buf)

    def __init__(self, buf, segment_offsets=None):
        # we need this empty init to silence this warning:
        # DeprecationWarning: object.__init__() takes no parameters
        pass

    @cython.final
    cdef inline check_bounds(self, Py_ssize_t size, Py_ssize_t offset):
        # the bound check seems to introduce a 5-10% overhead when calling
        # read_int64 from Python. However, I expect the overhead to be
        # relatively much higher if you call it from C. In case it's needed,
        # consider adding a read_int64_fast or similar method, which does
        # *not* do the check.
        cdef Py_ssize_t buflen = PyString_GET_SIZE(self.buf)
        if offset < 0 or offset + size > buflen:
            raise IndexError('Offset out of bounds: %d' % (offset+size))

    @cython.final
    cdef object read_primitive(self, Py_ssize_t offset, char ifmt):
        if ifmt == 'q':
            return self.read_int64(offset)
        elif ifmt == 'Q':
            return self.read_uint64_magic(offset)
        elif ifmt == 'd':
            return self.read_double(offset)
        elif ifmt == 'f':
            return self.read_float(offset)
        elif ifmt == 'i':
            return self.read_int32(offset)
        elif ifmt == 'I':
            return self.read_uint32(offset)
        elif ifmt == 'h':
            return self.read_int16(offset)
        elif ifmt == 'H':
            return self.read_uint16(offset)
        elif ifmt == 'b':
            return self.read_int8(offset)
        elif ifmt == 'B':
            return self.read_uint8(offset)
        raise ValueError('unknown fmt %s' % chr(ifmt))

    @cython.final
    cdef int64_t read_int64(self, Py_ssize_t offset) except? 0x7fffffffffffffff:
        self.check_bounds(8, offset)
        return (<int64_t*>(self.cbuf+offset))[0]

    @cython.final
    cdef uint64_t read_uint64(self, Py_ssize_t offset) except? 0xffffffffffffffff:
        self.check_bounds(8, offset)
        return (<uint64_t*>(self.cbuf+offset))[0]

    @cython.final
    cdef object read_uint64_magic(self, Py_ssize_t offset):
        # Special version of read_uint64; it returns a PyObject* instead of a
        # typed object (so it should be called only if the return value is
        # going to be converted to object anyway).  If the value is small
        # enough, it returns a python int. Else, a python long
        self.check_bounds(8, offset)
        uint64_value = (<uint64_t*>(self.cbuf+offset))[0]
        if uint64_value <= INT64_MAX:
            return <int64_t>uint64_value
        else:
            return uint64_value

    @cython.final
    cdef int32_t read_int32(self, Py_ssize_t offset) except? 0x7fffffff:
        self.check_bounds(4, offset)
        return (<int32_t*>(self.cbuf+offset))[0]

    @cython.final
    cdef uint32_t read_uint32(self, Py_ssize_t offset) except? 0xffffffff:
        self.check_bounds(4, offset)
        return (<uint32_t*>(self.cbuf+offset))[0]

    @cython.final
    cdef int16_t read_int16(self, Py_ssize_t offset) except? 0x7fff:
        self.check_bounds(2, offset)
        return (<int16_t*>(self.cbuf+offset))[0]

    @cython.final
    cdef uint16_t read_uint16(self, Py_ssize_t offset) except? 0xffff:
        self.check_bounds(2, offset)
        return (<uint16_t*>(self.cbuf+offset))[0]

    @cython.final
    cdef int8_t read_int8(self, Py_ssize_t offset) except? 0x7f:
        self.check_bounds(1, offset)
        return (<int8_t*>(self.cbuf+offset))[0]

    @cython.final
    cdef uint8_t read_uint8(self, Py_ssize_t offset) except? 0xff:
        self.check_bounds(1, offset)
        return (<uint8_t*>(self.cbuf+offset))[0]

    @cython.final
    cdef double read_double(self, Py_ssize_t offset) except? -1:
        self.check_bounds(8, offset)
        return (<double*>(self.cbuf+offset))[0]

    @cython.final
    cdef float read_float(self, Py_ssize_t offset) except? -1:
        self.check_bounds(4, offset)
        return (<float*>(self.cbuf+offset))[0]

    @cython.final
    cdef object dump_message(self, long p, Py_ssize_t start, Py_ssize_t end):
        cdef Py_ssize_t maxlen = PyString_GET_SIZE(self.buf)
        if start < 0 or start > end or end > maxlen:
            raise ValueError("start:end values out of bounds: %s:%s" %
                             (start, end))
        # XXX check start and end
        cdef long segment_count = 1
        cdef Py_ssize_t length = end-start
        cdef bytes buf = PyString_FromStringAndSize(NULL, length + 16)
        cdef char *cbuf = PyString_AS_STRING(buf)
        (<int32_t*>(cbuf+0))[0] = segment_count-1
        (<int32_t*>(cbuf+4))[0] = length/8 + 1 # in words
        (<int64_t*>(cbuf+8))[0] = p
        memcpy(cbuf+16, self.cbuf+start, end-start)
        return buf


cdef class BaseSegmentForTests(object):
    """
    All the BaseSegment's methods are "final cdef", and thus you cannot call them
    from Python. This class is a just a wrapper to be able to call them from
    tests
    """
    cdef BaseSegment s

    def __cinit__(self, bytes buf):
        self.s = BaseSegment(buf)

    def read_primitive(self, Py_ssize_t offset, char ifmt):
        return self.s.read_primitive(offset, ifmt)

    def read_int64(self, Py_ssize_t offset):
        return self.s.read_int64(offset)

    def read_uint64(self, Py_ssize_t offset):
        return self.s.read_uint64(offset)

    def read_uint64_magic(self, Py_ssize_t offset):
        return self.s.read_uint64_magic(offset)

    def read_int32(self, Py_ssize_t offset):
        return self.s.read_int32(offset)

    def read_uint32(self, Py_ssize_t offset):
        return self.s.read_uint32(offset)

    def read_int16(self, Py_ssize_t offset):
        return self.s.read_int16(offset)

    def read_uint16(self, Py_ssize_t offset):
        return self.s.read_uint16(offset)

    def read_int8(self, Py_ssize_t offset):
        return self.s.read_int8(offset)

    def read_uint8(self, Py_ssize_t offset):
        return self.s.read_uint8(offset)

    def read_double(self, Py_ssize_t offset):
        return self.s.read_double(offset)

    def read_float(self, Py_ssize_t offset):
        return self.s.read_float(offset)

    def dump_message(self, long p, Py_ssize_t start, Py_ssize_t end):
        return self.s.dump_message(p, start, end)
