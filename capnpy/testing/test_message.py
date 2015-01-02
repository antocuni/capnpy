from capnpy.message import Message, loads
from capnpy.blob import Blob, Types

def test_Message():
    buf = ('\x00\x00\x00\x00\x02\x00\x00\x00'   # ptr to anonymous struct
           '\x00\x00\x00\x00\x02\x00\x01\x00'   # ptr to payload (Point {x, y})
           '\x01\x00\x00\x00\x00\x00\x00\x00'   # x == 1
           '\x02\x00\x00\x00\x00\x00\x00\x00')  # y == 2
    m = Message(buf)
    p = m.get_struct(Blob)
    assert p._read_primitive(0, Types.int64) == 1
    assert p._read_primitive(8, Types.int64) == 2
    #
    p = loads(buf, Blob)
    assert isinstance(p, Blob)
    assert p._read_primitive(0, Types.int64) == 1
    assert p._read_primitive(8, Types.int64) == 2
