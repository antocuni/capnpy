import pytest
import sys
import struct
import math
from pypytools import IS_PYPY
from six import b, PY3

from capnpy import ptr
from capnpy.printer import print_buffer
from capnpy.segment.base import BaseSegmentForTests as BaseSegment, unpack_uint32

def test_unpack_uint32():
    a = 12
    b = 2**31 + 1
    buf = struct.pack('II', a, b)
    assert unpack_uint32(buf, 0) == a
    assert unpack_uint32(buf, 4) == b
    buf = b'abc'
    with pytest.raises(IndexError):
        unpack_uint32(buf, 0)


class TestBaseSegment(object):

    def test_None(self):
        with pytest.raises(AssertionError):
            BaseSegment(None)

    def test_read_int64(self):
        buf = struct.pack('qqq', 42, 43, 44)
        s = BaseSegment(buf)
        assert s.read_int64(0) == 42
        assert s.read_int64(8) == 43
        assert s.read_int64(16) == 44

    def test_read_ints(self):
        buf = b'garbage0' + b'\xff' * 8
        s = BaseSegment(buf)
        assert s.read_int8(8) == -1
        assert s.read_int16(8) == -1
        assert s.read_int32(8) == -1
        assert s.read_int64(8) == -1
        #
        assert s.read_uint8(8)  == (1 <<  8) - 1
        assert s.read_uint16(8) == (1 << 16) - 1
        assert s.read_uint32(8) == (1 << 32) - 1
        assert s.read_uint64(8) == (1 << 64) - 1

    def test_read_float(self):
        buf = struct.pack('ff', 0, math.pi)
        s = BaseSegment(buf)
        assert s.read_float(4) == struct.unpack('ff', buf)[1]

    def test_read_double(self):
        buf = struct.pack('dd', 0, math.pi)
        s = BaseSegment(buf)
        assert s.read_double(8) == struct.unpack('dd', buf)[1]

    def test_uint64(self):
        if sys.maxsize != (1 << 63)-1:
            pytest.skip('64 bit only')
        if IS_PYPY and sys.pypy_version_info < (5, 6):
            pytest.skip('Broken on PyPy<5.6')
        #
        buf = struct.pack('QQ', sys.maxsize, sys.maxsize+1)
        s = BaseSegment(buf)
        #
        val = s.read_uint64_magic(0)
        assert val == sys.maxsize == s.read_uint64(0)
        assert type(val) is int
        #
        val = s.read_primitive(0, ord('Q'))
        assert val == sys.maxsize == s.read_uint64(0)
        assert type(val) is int
        #
        val = s.read_uint64_magic(8)
        assert val == sys.maxsize+1 == s.read_uint64(8)
        if PY3:
            assert type(val) is int
        else:
            assert type(val) is long

    def test_read_primitive(self):
        buf = struct.pack('Q', 0x1234567887654321)
        s = BaseSegment(buf)
        for fmt in 'qQiIhHbBdf':
            val = s.read_primitive(0, ord(fmt))
            val2 = struct.unpack_from(fmt, buf, 0)[0]
            assert val == val2

    def test_errors(self):
        buf = b'\xff' * 8
        s = BaseSegment(buf)
        with pytest.raises(IndexError): s.read_int8(-1)
        with pytest.raises(IndexError): s.read_int16(-1)
        with pytest.raises(IndexError): s.read_int32(-1)
        with pytest.raises(IndexError): s.read_int64(-1)
        #
        with pytest.raises(IndexError): s.read_uint8(-1)
        with pytest.raises(IndexError): s.read_uint16(-1)
        with pytest.raises(IndexError): s.read_uint32(-1)
        with pytest.raises(IndexError): s.read_uint64(-1)
        #
        with pytest.raises(IndexError): s.read_float(-1)
        with pytest.raises(IndexError): s.read_double(-1)
        #
        with pytest.raises(IndexError): s.read_int64(8)

    def test_dump_message(self):
        buf = b('garbage0'
                '\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
                '\x02\x00\x00\x00\x00\x00\x00\x00'  # 2
                'garbage1')
        s = BaseSegment(buf)
        p = 0x12345678
        # segment header:
        #     segment_count-1: 0
        #     segment[0]_length: 3 (words)
        exp = b('\x00\x00\x00\x00\x03\x00\x00\x00'  # segment header
                '\x78\x56\x34\x12\x00\x00\x00\x00'  # p
                '\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
                '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
        msg = s.dump_message(p, 8, 24)
        assert msg == exp

    def test_dump_message_errors(self):
        buf = b('garbage0'
                '\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
                '\x02\x00\x00\x00\x00\x00\x00\x00'  # 2
                'garbage1')
        s = BaseSegment(buf)
        with pytest.raises(ValueError): s.dump_message(0, -1,  8)
        with pytest.raises(ValueError): s.dump_message(0, 32,  8)
        with pytest.raises(ValueError): s.dump_message(0,  8, -1)
        with pytest.raises(ValueError): s.dump_message(0,  8, 33)
        with pytest.raises(ValueError): s.dump_message(0, 16,  8)
