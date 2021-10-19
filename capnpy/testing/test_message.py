import pytest
from io import BytesIO
from six import b, PY3
from capnpy.message import load, loads, load_all, _load_message, dumps
from capnpy.filelike import as_filelike
from capnpy.type import Types
from capnpy.struct_ import Struct
from capnpy.printer import print_buffer

def test_load():
    buf = b('\x00\x00\x00\x00\x03\x00\x00\x00'   # message header: 1 segment, size 3 words
            '\x00\x00\x00\x00\x02\x00\x00\x00'   # ptr to payload (Point {x, y})
            '\x01\x00\x00\x00\x00\x00\x00\x00'   # x == 1
            '\x02\x00\x00\x00\x00\x00\x00\x00')  # y == 2
    f = BytesIO(buf)
    p = load(f, Struct)
    assert isinstance(p, Struct)
    assert p._read_primitive(0, Types.int64.ifmt) == 1
    assert p._read_primitive(8, Types.int64.ifmt) == 2

def _get_many_messages():
    one = b('\x00\x00\x00\x00\x03\x00\x00\x00'   # message header: 1 segment, size 3 words
            '\x00\x00\x00\x00\x02\x00\x00\x00'   # ptr to payload (Point {x, y})
            '\x01\x00\x00\x00\x00\x00\x00\x00'   # x == 1
            '\x02\x00\x00\x00\x00\x00\x00\x00')  # y == 2
    two = b('\x00\x00\x00\x00\x03\x00\x00\x00'   # message header: 1 segment, size 3 words
            '\x00\x00\x00\x00\x02\x00\x00\x00'   # ptr to payload (Point {x, y})
            '\x03\x00\x00\x00\x00\x00\x00\x00'   # x == 1
            '\x04\x00\x00\x00\x00\x00\x00\x00')  # y == 2
    return BytesIO(one+two)

def test_load_multiple_messages():
    f = _get_many_messages()
    p1 = load(f, Struct)
    assert p1._read_primitive(0, Types.int64.ifmt) == 1
    assert p1._read_primitive(8, Types.int64.ifmt) == 2
    p2 = load(f, Struct)
    assert p2._read_primitive(0, Types.int64.ifmt) == 3
    assert p2._read_primitive(8, Types.int64.ifmt) == 4

def test_load_all():
    f = _get_many_messages()
    messages = list(load_all(f, Struct))
    assert len(messages) == 2
    p1, p2 = messages
    #
    assert p1._read_primitive(0, Types.int64.ifmt) == 1
    assert p1._read_primitive(8, Types.int64.ifmt) == 2
    assert p2._read_primitive(0, Types.int64.ifmt) == 3
    assert p2._read_primitive(8, Types.int64.ifmt) == 4


def test_loads():
    buf = b('\x00\x00\x00\x00\x03\x00\x00\x00'   # message header: 1 segment, size 3 words
            '\x00\x00\x00\x00\x02\x00\x00\x00'   # ptr to payload (Point {x, y})
            '\x01\x00\x00\x00\x00\x00\x00\x00'   # x == 1
            '\x02\x00\x00\x00\x00\x00\x00\x00')  # y == 2

    p = loads(buf, Struct)
    assert isinstance(p, Struct)
    assert p._read_primitive(0, Types.int64.ifmt) == 1
    assert p._read_primitive(8, Types.int64.ifmt) == 2

def test_loads_not_whole_string():
    buf = b('\x00\x00\x00\x00\x03\x00\x00\x00'   # message header: 1 segment, size 3 words
            '\x00\x00\x00\x00\x02\x00\x00\x00'   # ptr to payload (Point {x, y})
            '\x01\x00\x00\x00\x00\x00\x00\x00'   # x == 1
            '\x02\x00\x00\x00\x00\x00\x00\x00'   # y == 2
            'garbage0')
    with pytest.raises(ValueError) as exc:
        p = loads(buf, Struct)
    assert str(exc.value) == 'Not all bytes were consumed: 8 bytes left'

def test_truncated_header_1():
    buf = b('\x03\x00\x00')  # we expect at least 4 bytes
    with pytest.raises(ValueError) as exc:
        p = loads(buf, Struct)
    assert str(exc.value) == 'Malformed header: expected 4 bytes, got 3'

def test_truncated_header_2():
    buf = b('\x03\x00\x00\x00'  # 3+1 segments, but only two are specified
            '\x10\x00\x00\x00'  # size0: 16
            '\x20\x00\x00\x00') # size1: 32
    with pytest.raises(ValueError) as exc:
        p = loads(buf, Struct)
    assert str(exc.value) == 'Unexpected EOF when reading the header'

def test_huge_number_of_segments():
    buf = b'hello' # this corresponds to 1819043177 segments
    with pytest.raises(ValueError) as exc:
        loads(buf, Struct)
    assert str(exc.value) == 'Unexpected EOF when reading the header'

def test_wrong_size():
    buf = b('\x00\x00\x00\x00\x04\x00\x00\x00'   # message header: 1 segment, size 4 words
            '\x00\x00\x00\x00\x02\x00\x01\x00'   # ptr to payload (Point {x, y})
            '\x01\x00\x00\x00\x00\x00\x00\x00'   # x == 1
            '\x02\x00\x00\x00\x00\x00\x00\x00')  # y == 2
    with pytest.raises(ValueError) as exc:
        loads(buf, Struct)
    assert str(exc.value) == ("Unexpected EOF: expected 32 bytes, got only 24. "
                              "Segment size: 4")

def test_wrong_size_multiple_segments():
    buf = b('\x01\x00\x00\x00\x04\x00\x00\x00'   # message header: 2 segments: (4, 5)
            '\x05\x00\x00\x00\x00\x00\x00\x00'
            '\x00\x00\x00\x00\x02\x00\x01\x00'   # ptr to payload (Point {x, y})
            '\x01\x00\x00\x00\x00\x00\x00\x00'   # x == 1
            '\x02\x00\x00\x00\x00\x00\x00\x00')  # y == 2
    with pytest.raises(ValueError) as exc:
        loads(buf, Struct)
    assert str(exc.value) == ("Unexpected EOF: expected 72 bytes, got only 24. "
                              "Segments size: [4, 5]")

def test_eof():
    buf = b''
    with pytest.raises(EOFError):
        loads(buf, Struct)

def test_segments():
    header = b('\x03\x00\x00\x00'  # 3+1 segments
               '\x10\x00\x00\x00'  # size0: 16
               '\x20\x00\x00\x00'  # size1: 32
               '\x40\x00\x00\x00'  # size2: 64
               '\x10\x00\x00\x00'  # size3: 16
               '\x00\x00\x00\x00') # padding
    payload = b'\x00'*16*8 + b'\x00'*32*8 + b'\x00'*64*8 + b'\x00'*16*8
    buf = header + payload
    f = BytesIO(buf)
    msg = _load_message(as_filelike(f))
    assert f.tell() == len(buf)
    assert msg._data_offset == 0
    assert msg._seg.segment_offsets == (0, 16*8, (16+32)*8, (16+32+64)*8)
    assert msg._seg.buf == payload

def test_dumps():
    class Point(Struct):
        pass
    
    buf = b('\x01\x00\x00\x00\x00\x00\x00\x00'   # x == 1
            '\x02\x00\x00\x00\x00\x00\x00\x00')  # y == 2
    p = Point.from_buffer(buf, 0, data_size=2, ptrs_size=0)
    msg = dumps(p)
    exp = b('\x00\x00\x00\x00\x03\x00\x00\x00'   # message header: 1 segment, size 3 words
            '\x00\x00\x00\x00\x02\x00\x00\x00'   # ptr to payload (Point {x, y})
            '\x01\x00\x00\x00\x00\x00\x00\x00'   # x == 1
            '\x02\x00\x00\x00\x00\x00\x00\x00')  # y == 2
    assert msg == exp

def test_dumps_alignment():
    class Person(Struct):
        pass

    buf = b('\x20\x00\x00\x00\x00\x00\x00\x00'   # age=32
            '\x01\x00\x00\x00\x2a\x00\x00\x00'   # name=ptr
            'J' 'o' 'h' 'n' '\x00\x00\x00\x00')  # John

    p = Person.from_buffer(buf, 0, data_size=1, ptrs_size=1)
    msg = dumps(p)
    exp = b('\x00\x00\x00\x00\x04\x00\x00\x00'   # message header: 1 segment, size 3 words
            '\x00\x00\x00\x00\x01\x00\x01\x00'   # ptr to payload
            '\x20\x00\x00\x00\x00\x00\x00\x00'   # age=32
            '\x01\x00\x00\x00\x2a\x00\x00\x00'   # name=ptr
            'J' 'o' 'h' 'n' '\x00\x00\x00\x00')  # John
    assert msg == exp

def test_dumps_not_compact():
    class Person(Struct):
        pass

    buf = b('\x20\x00\x00\x00\x00\x00\x00\x00'   # age=32
            '\x05\x00\x00\x00\x2a\x00\x00\x00'   # name=ptr
            'garbage1'
            'J' 'o' 'h' 'n' '\x00\x00\x00\x00')  # John

    p = Person.from_buffer(buf, 0, data_size=1, ptrs_size=1)
    msg = dumps(p)
    exp = b('\x00\x00\x00\x00\x04\x00\x00\x00'   # message header: 1 segment, size 3 words
            '\x00\x00\x00\x00\x01\x00\x01\x00'   # ptr to payload
            '\x20\x00\x00\x00\x00\x00\x00\x00'   # age=32
            '\x01\x00\x00\x00\x2a\x00\x00\x00'   # name=ptr
            'J' 'o' 'h' 'n' '\x00\x00\x00\x00')  # John
    assert msg == exp


def test_Struct_loads():
    class Point(Struct):
        pass

    buf = b('\x00\x00\x00\x00\x03\x00\x00\x00'   # message header: 1 segment, size 3 words
            '\x00\x00\x00\x00\x02\x00\x00\x00'   # ptr to payload (Point {x, y})
            '\x01\x00\x00\x00\x00\x00\x00\x00'   # x == 1
            '\x02\x00\x00\x00\x00\x00\x00\x00')  # y == 2

    p = Point.loads(buf)
    assert isinstance(p, Point)
    assert p._read_primitive(0, Types.int64.ifmt) == 1
    assert p._read_primitive(8, Types.int64.ifmt) == 2

def test_Struct_dumps():
    class Point(Struct):
        pass

    buf = b('\x01\x00\x00\x00\x00\x00\x00\x00'   # x == 1
            '\x02\x00\x00\x00\x00\x00\x00\x00')  # y == 2
    p = Point.from_buffer(buf, 0, data_size=2, ptrs_size=0)
    msg = p.dumps()
    exp = b('\x00\x00\x00\x00\x03\x00\x00\x00'   # message header: 1 segment, size 3 words
            '\x00\x00\x00\x00\x02\x00\x00\x00'   # ptr to payload (Point {x, y})
            '\x01\x00\x00\x00\x00\x00\x00\x00'   # x == 1
            '\x02\x00\x00\x00\x00\x00\x00\x00')  # y == 2
    assert msg == exp

class TestFileLike(object):
    """
    Test that message.load work with various file-like objects
    """

    buf = b('\x00\x00\x00\x00\x03\x00\x00\x00'   # message header: 1 segment, size 3 words
            '\x00\x00\x00\x00\x02\x00\x00\x00'   # ptr to payload (Point {x, y})
            '\x01\x00\x00\x00\x00\x00\x00\x00'   # x == 1
            '\x02\x00\x00\x00\x00\x00\x00\x00')  # y == 2

    def check(self, f):
        p = load(f, Struct)
        assert isinstance(p, Struct)
        assert p._read_primitive(0, Types.int64.ifmt) == 1
        assert p._read_primitive(8, Types.int64.ifmt) == 2

    def test_BytesIO(self):
        f = BytesIO(self.buf)
        self.check(f)

    def test_file(self, tmpdir):
        myfile = tmpdir.join('myfile')
        myfile.write(self.buf)
        with myfile.open(mode='rb' if PY3 else 'r') as f:
            self.check(f)

    def test_socket(self):
        from capnpy.buffered import BufferedSocket
        def chunks(buf, n):
            for i in range(0, len(buf), n):
                yield buf[i:i+n]
            # now simulate closed socket
            while True:
                yield ''

        class FakeSocket(object):
            def __init__(self, buf):
                # yield packets 7 bytes at a time (to excercise BufferedSocket
                # corner cases)
                self._chunks = chunks(buf, 7)

            def recv(self, size):
                return next(self._chunks)

        sock = FakeSocket(self.buf)
        buffered_sock = BufferedSocket(sock)
        self.check(buffered_sock)
