import py
from capnpy.message import loads, _load_message
from capnpy.blob import Blob, Types

def test_loads():
    buf = ('\x00\x00\x00\x00\x03\x00\x00\x00'   # message header: 1 segment, size 3 words
           '\x00\x00\x00\x00\x02\x00\x01\x00'   # ptr to payload (Point {x, y})
           '\x01\x00\x00\x00\x00\x00\x00\x00'   # x == 1
           '\x02\x00\x00\x00\x00\x00\x00\x00')  # y == 2

    p = loads(buf, Blob)
    assert isinstance(p, Blob)
    assert p._read_primitive(0, Types.int64) == 1
    assert p._read_primitive(8, Types.int64) == 2

def test_wrong_size():
    buf = ('\x00\x00\x00\x00\x04\x00\x00\x00'   # message header: 1 segment, size 4 words
           '\x00\x00\x00\x00\x02\x00\x01\x00'   # ptr to payload (Point {x, y})
           '\x01\x00\x00\x00\x00\x00\x00\x00'   # x == 1
           '\x02\x00\x00\x00\x00\x00\x00\x00')  # y == 2
    py.test.raises(ValueError, "loads(buf, Blob)")


def test_segments():
    header = ('\x03\x00\x00\x00'  # 3+1 segments
              '\x10\x00\x00\x00'  # size0: 16
              '\x20\x00\x00\x00'  # size1: 32
              '\x40\x00\x00\x00'  # size2: 64
              '\x10\x00\x00\x00'  # size3: 16
              '\x00\x00\x00\x00') # padding
    buf = header + '\x00'*16*8 + '\x00'*32*8 + '\x00'*64*8 + '\x00'*16*8
    msg = _load_message(buf)
    assert msg._offset == 24
    assert msg._segment_offsets == (24, 24+16*8, 24+(16+32)*8, 24+(16+32+64)*8)
