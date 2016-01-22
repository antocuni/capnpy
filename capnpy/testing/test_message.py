import py
from cStringIO import StringIO
from capnpy.message import load, loads, _load_message, dumps
from capnpy.blob import Types
from capnpy.struct_ import Struct

def test_load():
    buf = ('\x00\x00\x00\x00\x03\x00\x00\x00'   # message header: 1 segment, size 3 words
           '\x00\x00\x00\x00\x02\x00\x00\x00'   # ptr to payload (Point {x, y})
           '\x01\x00\x00\x00\x00\x00\x00\x00'   # x == 1
           '\x02\x00\x00\x00\x00\x00\x00\x00')  # y == 2
    f = StringIO(buf)

    p = load(f, Struct)
    assert isinstance(p, Struct)
    assert p._read_data(0, Types.int64.ifmt) == 1
    assert p._read_data(8, Types.int64.ifmt) == 2

def test_load_multiple_messages():
    one = ('\x00\x00\x00\x00\x03\x00\x00\x00'   # message header: 1 segment, size 3 words
           '\x00\x00\x00\x00\x02\x00\x00\x00'   # ptr to payload (Point {x, y})
           '\x01\x00\x00\x00\x00\x00\x00\x00'   # x == 1
           '\x02\x00\x00\x00\x00\x00\x00\x00')  # y == 2
    two = ('\x00\x00\x00\x00\x03\x00\x00\x00'   # message header: 1 segment, size 3 words
           '\x00\x00\x00\x00\x02\x00\x00\x00'   # ptr to payload (Point {x, y})
           '\x03\x00\x00\x00\x00\x00\x00\x00'   # x == 1
           '\x04\x00\x00\x00\x00\x00\x00\x00')  # y == 2
    f = StringIO(one+two)
    p1 = load(f, Struct)
    assert p1._read_data(0, Types.int64.ifmt) == 1
    assert p1._read_data(8, Types.int64.ifmt) == 2
    p2 = load(f, Struct)
    assert p2._read_data(0, Types.int64.ifmt) == 3
    assert p2._read_data(8, Types.int64.ifmt) == 4

def test_loads():
    buf = ('\x00\x00\x00\x00\x03\x00\x00\x00'   # message header: 1 segment, size 3 words
           '\x00\x00\x00\x00\x02\x00\x00\x00'   # ptr to payload (Point {x, y})
           '\x01\x00\x00\x00\x00\x00\x00\x00'   # x == 1
           '\x02\x00\x00\x00\x00\x00\x00\x00')  # y == 2

    p = loads(buf, Struct)
    assert isinstance(p, Struct)
    assert p._read_data(0, Types.int64.ifmt) == 1
    assert p._read_data(8, Types.int64.ifmt) == 2

def test_loads_not_whole_string():
    buf = ('\x00\x00\x00\x00\x03\x00\x00\x00'   # message header: 1 segment, size 3 words
           '\x00\x00\x00\x00\x02\x00\x00\x00'   # ptr to payload (Point {x, y})
           '\x01\x00\x00\x00\x00\x00\x00\x00'   # x == 1
           '\x02\x00\x00\x00\x00\x00\x00\x00'   # y == 2
           'garbage0')
    exc = py.test.raises(ValueError, "p = loads(buf, Struct)")
    assert exc.value.message == 'Not all bytes were consumed: 8 bytes left'

def test_wrong_size():
    buf = ('\x00\x00\x00\x00\x04\x00\x00\x00'   # message header: 1 segment, size 4 words
           '\x00\x00\x00\x00\x02\x00\x01\x00'   # ptr to payload (Point {x, y})
           '\x01\x00\x00\x00\x00\x00\x00\x00'   # x == 1
           '\x02\x00\x00\x00\x00\x00\x00\x00')  # y == 2
    exc = py.test.raises(ValueError, "loads(buf, Struct)")
    assert exc.value.message == ("Unexpected EOF: expected 32 bytes, got only 24. "
                                 "Segments size: [4]")

def test_segments():
    header = ('\x03\x00\x00\x00'  # 3+1 segments
              '\x10\x00\x00\x00'  # size0: 16
              '\x20\x00\x00\x00'  # size1: 32
              '\x40\x00\x00\x00'  # size2: 64
              '\x10\x00\x00\x00'  # size3: 16
              '\x00\x00\x00\x00') # padding
    payload = '\x00'*16*8 + '\x00'*32*8 + '\x00'*64*8 + '\x00'*16*8
    buf = header + payload
    f = StringIO(buf)
    msg = _load_message(f)
    assert f.tell() == len(buf)
    assert msg._data_offset == 0
    assert msg._buf.segment_offsets == (0, 16*8, (16+32)*8, (16+32+64)*8)
    assert msg._buf.s == payload

def test_dumps():
    class Point(Struct):
        pass
    
    buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'   # x == 1
           '\x02\x00\x00\x00\x00\x00\x00\x00')  # y == 2
    p = Point.from_buffer(buf, 0, data_size=2, ptrs_size=0)
    msg = dumps(p)
    exp = ('\x00\x00\x00\x00\x03\x00\x00\x00'   # message header: 1 segment, size 3 words
           '\x00\x00\x00\x00\x02\x00\x00\x00'   # ptr to payload (Point {x, y})
           '\x01\x00\x00\x00\x00\x00\x00\x00'   # x == 1
           '\x02\x00\x00\x00\x00\x00\x00\x00')  # y == 2
    assert msg == exp

def test_dumps_alignment():
    class Person(Struct):
        pass

    buf = ('\x20\x00\x00\x00\x00\x00\x00\x00'   # age=32
           '\x01\x00\x00\x00\x2a\x00\x00\x00'   # name=ptr
           'J' 'o' 'h' 'n' '\x00\x00\x00\x00')  # John

    p = Person.from_buffer(buf, 0, data_size=1, ptrs_size=1)
    msg = dumps(p)
    exp = ('\x00\x00\x00\x00\x04\x00\x00\x00'   # message header: 1 segment, size 3 words
           '\x00\x00\x00\x00\x01\x00\x01\x00'   # ptr to payload
           '\x20\x00\x00\x00\x00\x00\x00\x00'   # age=32
           '\x01\x00\x00\x00\x2a\x00\x00\x00'   # name=ptr
           'J' 'o' 'h' 'n' '\x00\x00\x00\x00')  # John
    assert msg == exp
