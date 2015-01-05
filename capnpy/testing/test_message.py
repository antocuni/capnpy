import py
from capnpy.message import loads
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
