import py
from capnpy import ptr
from capnpy.type import Types
from capnpy.segment.segment import MultiSegment
from capnpy.struct_ import Struct, undefined
from capnpy.enum import enum
from capnpy.printer import print_buffer

## struct Point {
##   x @0 :Int64;
##   y @1 :Int64;
## }
##
## struct Rectangle {
##   color @0 :Int64;
##   a @1 :Point;
##   b @2 :Point;
## }
BUF = ('garbage0'
       '\x01\x00\x00\x00\x00\x00\x00\x00'    # color == 1
       '\x0c\x00\x00\x00\x02\x00\x00\x00'    # ptr to a
       '\x10\x00\x00\x00\x02\x00\x00\x00'    # ptr to b
       'garbage1'
       'garbage2'
       '\x01\x00\x00\x00\x00\x00\x00\x00'    # a.x == 1
       '\x02\x00\x00\x00\x00\x00\x00\x00'    # a.y == 2
       '\x03\x00\x00\x00\x00\x00\x00\x00'    # b.x == 3
       '\x04\x00\x00\x00\x00\x00\x00\x00')   # b.y == 4

def test_undefined():
    assert repr(undefined) == '<undefined>'

def test__as_pointer():
    buf = ('garbage0'
           '\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
           '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
    b1 = Struct.from_buffer(buf, 8, data_size=2, ptrs_size=0)
    p = b1._as_pointer(24) # arbitrary offset
    assert ptr.kind(p) == ptr.STRUCT
    assert ptr.deref(p, 24) == 8
    assert ptr.struct_data_size(p) == 2
    assert ptr.struct_ptrs_size(p) == 0

def test__read_data():
    buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
           '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
    b1 = Struct.from_buffer(buf, 0, data_size=2, ptrs_size=0)
    assert b1._read_data(0, Types.int64.ifmt) == 1
    assert b1._read_data(8, Types.int64.ifmt) == 2
    assert b1._read_data(16, Types.int64.ifmt) == 0 # outside the buffer

def test__read_struct():
    ## struct Point {
    ##   x @0 :Int64;
    ##   y @1 :Int64;
    ## }
    buf = ('\x00\x00\x00\x00\x02\x00\x00\x00'    # ptr to {x, y}
           '\x01\x00\x00\x00\x00\x00\x00\x00'    # x == 1
           '\x02\x00\x00\x00\x00\x00\x00\x00')   # y == 2
    s = Struct.from_buffer(buf, 0, data_size=0, ptrs_size=1)
    p = s._read_struct(0, Struct)
    assert p._seg is s._seg
    assert p._data_offset == 8
    assert p._data_size == 2
    assert p._ptrs_size == 0
    assert p._read_data(0, Types.int64.ifmt) == 1
    assert p._read_data(8, Types.int64.ifmt) == 2

def test__read_struct_with_offset():
    ## struct Point {
    ##   x @0 :Int64;
    ##   y @1 :Int64;
    ## }
    buf = ('abcd'                                # garbage
           '\x00\x00\x00\x00\x02\x00\x00\x00'    # ptr to {x, y}
           '\x01\x00\x00\x00\x00\x00\x00\x00'    # x == 1
           '\x02\x00\x00\x00\x00\x00\x00\x00')   # y == 2
    s = Struct.from_buffer(buf, 4, data_size=0, ptrs_size=1)
    p = s._read_struct(0, Struct)
    assert p._seg is s._seg
    assert p._data_offset == 12
    assert p._data_size == 2
    assert p._ptrs_size == 0
    assert p._read_data(0, Types.int64.ifmt) == 1
    assert p._read_data(8, Types.int64.ifmt) == 2


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
    rect = Struct.from_buffer(buf, 0, data_size=0, ptrs_size=2)
    p1 = rect._read_struct(0, Struct)
    p2 = rect._read_struct(8, Struct)
    assert p1._read_data(0, Types.int64.ifmt) == 1
    assert p1._read_data(8, Types.int64.ifmt) == 2
    assert p2._read_data(0, Types.int64.ifmt) == 3
    assert p2._read_data(8, Types.int64.ifmt) == 4

def test_null_pointers():
    buf = '\x00\x00\x00\x00\x00\x00\x00\x00'    # NULL pointer
    blob = Struct.from_buffer(buf, 0, data_size=0, ptrs_size=1)
    assert blob._read_list(0, None, None) is None
    assert blob._read_str_text(0) is None
    assert blob._read_struct(0, Struct) is None
    #
    val = 'dummy default value'
    assert blob._read_list(0, None, default_=val) is val
    assert blob._read_str_text(0, default_=val) is val


def test_far_pointer():
    # see also test_list.test_far_pointer
    seg0 = ('\x00\x00\x00\x00\x00\x00\x00\x00'    # some garbage
            '\x0a\x00\x00\x00\x01\x00\x00\x00')   # far pointer: segment=1, offset=1
    seg1 = ('\x00\x00\x00\x00\x00\x00\x00\x00'    # random data
            '\x00\x00\x00\x00\x02\x00\x00\x00'    # ptr to {x, y}
            '\x01\x00\x00\x00\x00\x00\x00\x00'    # x == 1
            '\x02\x00\x00\x00\x00\x00\x00\x00')   # y == 2
    #
    buf = MultiSegment(seg0+seg1, segment_offsets=(0, 16))
    blob = Struct.from_buffer(buf, 8, data_size=0, ptrs_size=1)
    p = blob._read_struct(0, Struct)
    assert p._read_data(0, Types.int64.ifmt) == 1
    assert p._read_data(8, Types.int64.ifmt) == 2

def test_union():
    ## struct Shape {
    ##   area @0 :Int64;
    ##   union {
    ##     circle @1 :Int64;      # radius
    ##     square @2 :Int64;      # width
    ##   }
    ## }
    class Shape(Struct):
        __tag_offset__ = 16
        __tag__ = enum('Shape.__tag__', ('circle', 'square'))
    
    buf = ('\x40\x00\x00\x00\x00\x00\x00\x00'     # area == 64
           '\x08\x00\x00\x00\x00\x00\x00\x00'     # square == 8
           '\x01\x00\x00\x00\x00\x00\x00\x00')    # which() == square, padding
    shape = Shape.from_buffer(buf, 0, data_size=3, ptrs_size=0)
    w = shape.which()
    assert type(w) is Shape.__tag__
    assert w == Shape.__tag__.square
    w = shape.__which__()
    assert type(w) is int
    assert w == Shape.__tag__.square
    #
    shape._ensure_union(Shape.__tag__.square)
    py.test.raises(ValueError, "shape._ensure_union(Shape.__tag__.circle)")


def test_compact():
    class Rect(Struct):
        pass

    buf = ('garbage0'
           '\x01\x00\x00\x00\x00\x00\x00\x00'    # color == 1
           '\x0c\x00\x00\x00\x02\x00\x00\x00'    # ptr to a
           '\x00\x00\x00\x00\x00\x00\x00\x00'    # ptr to b, NULL
           'garbage1'
           'garbage2'
           '\x01\x00\x00\x00\x00\x00\x00\x00'    # a.x == 1
           '\x02\x00\x00\x00\x00\x00\x00\x00')   # a.y == 2
    rect = Rect.from_buffer(buf, 8, data_size=1, ptrs_size=2)
    rect2 = rect.compact()
    assert rect2.__class__ is Rect
    buf = rect2._seg.buf[rect2._data_offset:]
    assert buf == ('\x01\x00\x00\x00\x00\x00\x00\x00'    # color == 1
                   '\x04\x00\x00\x00\x02\x00\x00\x00'    # ptr to a
                   '\x00\x00\x00\x00\x00\x00\x00\x00'    # ptr to b, NULL
                   '\x01\x00\x00\x00\x00\x00\x00\x00'    # a.x == 1
                   '\x02\x00\x00\x00\x00\x00\x00\x00')   # a.y == 2

def test_comparisons_fail():
    s = Struct.from_buffer('', 0, data_size=0, ptrs_size=0)
    py.test.raises(TypeError, "hash(s)")
    py.test.raises(TypeError, "s == s")
    py.test.raises(TypeError, "s != s")
    py.test.raises(TypeError, "s < s")
    py.test.raises(TypeError, "s <= s")
    py.test.raises(TypeError, "s > s")
    py.test.raises(TypeError, "s >= s")

def test_comparisons_succeed():
    class MyStruct(Struct):
        def __hash__(self):
            return 1234

        def _equals(self, other):
            # dummy, random implementation
            return self._seg.buf == other._seg.buf
    #
    s1 = MyStruct.from_buffer('', 0, data_size=0, ptrs_size=0)
    s2 = MyStruct.from_buffer('', 0, data_size=0, ptrs_size=0)
    s3 = MyStruct.from_buffer('x', 0, data_size=0, ptrs_size=0)
    assert hash(s1) == 1234
    assert s1 == s2
    assert s1 != s3
    py.test.raises(TypeError, "s1 < s2")
    py.test.raises(TypeError, "s1 <= s2")
    py.test.raises(TypeError, "s1 > s2")
    py.test.raises(TypeError, "s1 >= s2")

def test_check_null_buffer():
    py.test.raises(AssertionError, "Struct(None, 0, 0, 0)")
