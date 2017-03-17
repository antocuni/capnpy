import py
import pytest
import sys
import struct
import math
from pypytools import IS_PYPY
from capnpy.packing import (unpack_primitive, pack_message_header, pack_into)


class TestUnpack(object):

    def test_unpack_primitive_ints(self):
        buf = '\xff' * 8
        assert unpack_primitive(ord('b'), buf, 0) == -1
        assert unpack_primitive(ord('h'), buf, 0) == -1
        assert unpack_primitive(ord('i'), buf, 0) == -1
        assert unpack_primitive(ord('q'), buf, 0) == -1
        #
        assert unpack_primitive(ord('B'), buf, 0) == (1 <<  8) - 1
        assert unpack_primitive(ord('H'), buf, 0) == (1 << 16) - 1
        assert unpack_primitive(ord('I'), buf, 0) == (1 << 32) - 1
        assert unpack_primitive(ord('Q'), buf, 0) == (1 << 64) - 1

    def test_unpack_primitive_floats(self):
        buf = struct.pack('f', math.pi)
        assert unpack_primitive(ord('f'), buf, 0) == struct.unpack('f', buf)[0]
        #
        buf = struct.pack('d', math.pi)
        assert unpack_primitive(ord('d'), buf, 0) == struct.unpack('d', buf)[0]

    def test_uint64(self):
        if sys.maxint != (1 << 63)-1:
            py.test.skip('64 bit only')
        if IS_PYPY and sys.pypy_version_info < (5, 6):
            py.test.skip('Broken on PyPy<5.6')
        #
        buf = struct.pack('Q', sys.maxint)
        val = unpack_primitive(ord('Q'), buf, 0)
        assert val == sys.maxint
        assert type(val) is int
        #
        buf = struct.pack('Q', sys.maxint+1)
        val = unpack_primitive(ord('Q'), buf, 0)
        assert val == sys.maxint+1
        assert type(val) is long

    def test_bytearray(self):
        buf = bytearray(struct.pack('q', 42))
        assert unpack_primitive(ord('q'), buf, 0) == 42

    def test_errors(self):
        buf = '\xff' * 8
        pytest.raises(IndexError, "unpack_primitive(ord('q'), buf, -1)")
        pytest.raises(IndexError, "unpack_primitive(ord('q'), buf, 8)")
        pytest.raises(TypeError, "unpack_primitive(ord('q'), 42, 0)")


class TestPack(object):

    def check(self, fmt, value):
        from random import randrange
        # build a buffer which is surely big enough to contain what we need
        # and check:
        #   1) that we correctly write the bytes we expect
        #   2) that we do NOT write outside the bounds
        #
        pattern = [chr(randrange(256)) for _ in range(256)]
        pattern = ''.join(pattern)
        buf = bytearray(pattern)
        buf2 = bytearray(pattern)
        offset = 16
        pack_into(ord(fmt), buf, offset, value)
        struct.pack_into(fmt, buf2, offset, value)
        assert buf == buf2
        #
        # check that it raises if it's out of bound
        out_of_bound = 256-struct.calcsize(fmt)+1
        pytest.raises(IndexError, "pack_into(ord(fmt), buf, out_of_bound, value)")

    def test_pack_into(self):
        self.check('b', 2**7 - 1)
        self.check('B', 2**8 - 1)
        self.check('h', 2**15 - 1)
        self.check('H', 2**16 - 1)
        self.check('i', 2**31 - 1)
        self.check('I', 2**32 - 1)
        self.check('q', 2**63 - 1)
        self.check('Q', 2**64 - 1)
        self.check('f', 1.234)
        self.check('d', 1.234)


def test_pack_message_header():
    header = pack_message_header(1, 0xAA, 0xBBCCDD)
    assert header == ('\x00\x00\x00\x00'
                      '\xaa\x00\x00\x00'
                      '\xdd\xcc\xbb\x00\x00\x00\x00\x00')
