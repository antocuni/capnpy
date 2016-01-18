import py
import struct
from capnpy.blob import CapnpBuffer, Blob, Types, unpack_primitive
from capnpy.struct_ import Struct

class BlobForTests(Blob):

    def __init__(self, buf, offset):
        Blob.__init__(self, buf)
        self._offset = offset

    def _read_data(self, offset, t):
        return self._buf.read_primitive(self._offset+offset, t)

    def _read_ptr(self, offset):
        return self._buf.read_ptr(self._offset+offset)


def test_unpack_primitive():
    s = struct.pack('q', 1234)
    assert unpack_primitive('q', s, 0) == 1234
    #
    # left bound check
    with py.test.raises(IndexError):
        unpack_primitive('q', s, -8)
    #
    # right bound check
    with py.test.raises(IndexError):
        unpack_primitive('q', s, 1) # not enough bytes


def test_CapnpBuffer():
    # buf is an array of int64 == [1, 2]
    buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
           '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
    b1 = CapnpBuffer(buf, None)
    assert b1.read_primitive(0, Types.int64) == 1
    assert b1.read_primitive(8, Types.int64) == 2


def test_float64():
    buf = '\x58\x39\xb4\xc8\x76\xbe\xf3\x3f'   # 1.234
    b = CapnpBuffer(buf, None)
    assert b.read_primitive(0, Types.float64) == 1.234

def test_read_ptr():
    buf = '\x90\x01\x00\x00\x02\x00\x04\x00'
    b = CapnpBuffer(buf, None)
    offset, ptr = b.read_ptr(0)
    offset = ptr.deref(offset)
    assert offset == 808

def test_read_struct():
    ## struct Point {
    ##   x @0 :Int64;
    ##   y @1 :Int64;
    ## }
    buf = ('\x00\x00\x00\x00\x02\x00\x00\x00'    # ptr to {x, y}
           '\x01\x00\x00\x00\x00\x00\x00\x00'    # x == 1
           '\x02\x00\x00\x00\x00\x00\x00\x00')   # y == 2
    blob = BlobForTests(buf, 0)
    p = blob._read_struct(0, Struct)
    assert p._buf is blob._buf
    assert p._data_offset == 8
    assert p._data_size == 2
    assert p._ptrs_size == 0
    assert p._read_data(0, Types.int64) == 1
    assert p._read_data(8, Types.int64) == 2

def test_nested_struct():
    ## struct Rectangle {
    ##   a @0 :Point;
    ##   b @1 :Point;
    ## }
    buf = ('\x04\x00\x00\x00\x02\x00\x00\x00'    # ptr to a
           '\x08\x00\x00\x00\x02\x00\x00\x00'    # ptr to b
           '\x01\x00\x00\x00\x00\x00\x00\x00'    # a.x == 1
           '\x02\x00\x00\x00\x00\x00\x00\x00'    # a.y == 2
           '\x03\x00\x00\x00\x00\x00\x00\x00'    # b.x == 3
           '\x04\x00\x00\x00\x00\x00\x00\x00')   # b.y == 4
    rect = BlobForTests(buf, 0)
    p1 = rect._read_struct(0, Struct)
    p2 = rect._read_struct(8, Struct)
    assert p1._read_data(0, Types.int64) == 1
    assert p1._read_data(8, Types.int64) == 2
    assert p2._read_data(0, Types.int64) == 3
    assert p2._read_data(8, Types.int64) == 4
    

def test_null_pointers():
    buf = '\x00\x00\x00\x00\x00\x00\x00\x00'    # NULL pointer
    blob = BlobForTests(buf, 0)
    assert blob._read_list(0, None, None) is None
    assert blob._read_string(0) is None
    assert blob._read_struct(0, Struct) is None
    assert blob._read_list_or_struct(0) is None
    #
    val = 'dummy default value'
    assert blob._read_list(0, None, None, default_=val) is val
    assert blob._read_string(0, default_=val) is val
    assert blob._read_struct(0, Struct, default_=val) is val
    assert blob._read_list_or_struct(0, default_=val) is val


def test_read_group():
    ## struct Rectangle {
    ##     a @0 :group {
    ##         x @1 :Int64;
    ##         y @2 :Int64;
    ##     }
    ##     b @3 :group {
    ##         x @4 :Int64;
    ##         y @5 :Int64;
    ##     }
    ## }
    class GroupA(Struct):
        pass
    class GroupB(Struct):
        pass
    buf = ('garbage0'
           '\x01\x00\x00\x00\x00\x00\x00\x00'    # a.x == 1
           '\x02\x00\x00\x00\x00\x00\x00\x00'    # a.y == 2
           '\x03\x00\x00\x00\x00\x00\x00\x00'    # b.x == 3
           '\x04\x00\x00\x00\x00\x00\x00\x00')   # b.y == 4
    #
    # Note that the offsets inside groups are always "absolute" from the
    # beginning of the struct. So, a.x has offset 0, b.x has offset 3.
    #
    blob = Struct.from_buffer(buf, 8, data_size=4, ptrs_size=0)
    a = blob._read_group(GroupA)
    assert isinstance(a, GroupA)
    assert a._data_size == 4
    assert a._ptrs_size == 0
    assert a._read_data(0, Types.int64) == 1  # a.x
    #
    b = blob._read_group(GroupB)
    assert isinstance(b, GroupB)
    assert b._data_size == 4
    assert b._ptrs_size == 0
    assert b._read_data(16, Types.int64) == 3 # b.x


def test_far_pointer():
    # see also test_list.test_far_pointer
    seg0 = ('\x00\x00\x00\x00\x00\x00\x00\x00'    # some garbage
            '\x0a\x00\x00\x00\x01\x00\x00\x00')   # far pointer: segment=1, offset=1
    seg1 = ('\x00\x00\x00\x00\x00\x00\x00\x00'    # random data
            '\x00\x00\x00\x00\x02\x00\x00\x00'    # ptr to {x, y}
            '\x01\x00\x00\x00\x00\x00\x00\x00'    # x == 1
            '\x02\x00\x00\x00\x00\x00\x00\x00')   # y == 2
    #
    buf = CapnpBuffer(seg0+seg1, segment_offsets=(0, 16))
    blob = BlobForTests(buf, 8)
    p = blob._read_struct(0, Struct)
    assert p._read_data(0, Types.int64) == 1
    assert p._read_data(8, Types.int64) == 2
