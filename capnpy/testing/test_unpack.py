import py
import pytest
import sys
import struct
import math
from pypytools import IS_PYPY
from capnpy.unpack import unpack_primitive, pack_message_header

def test_unpack_primitive_ints():
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
    
def test_unpack_primitive_floats():
    buf = struct.pack('f', math.pi)
    assert unpack_primitive(ord('f'), buf, 0) == struct.unpack('f', buf)[0]
    #
    buf = struct.pack('d', math.pi)
    assert unpack_primitive(ord('d'), buf, 0) == struct.unpack('d', buf)[0]

def test_uint64():
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

def test_bytearray():
    buf = bytearray(struct.pack('q', 42))
    assert unpack_primitive(ord('q'), buf, 0) == 42

def test_errors():
    buf = '\xff' * 8
    pytest.raises(IndexError, "unpack_primitive(ord('q'), buf, -1)")
    pytest.raises(IndexError, "unpack_primitive(ord('q'), buf, 8)")
    pytest.raises(TypeError, "unpack_primitive(ord('q'), 42, 0)")

def test_pack_message_header():
    header = pack_message_header(1, 0xAA, 0xBBCCDD)
    assert header == ('\x00\x00\x00\x00'
                      '\xaa\x00\x00\x00'
                      '\xdd\xcc\xbb\x00\x00\x00\x00\x00')
