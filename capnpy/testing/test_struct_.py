# -*- encoding: utf-8 -*-

import pytest
from six import b, PY3

from capnpy import ptr
from capnpy.type import Types
from capnpy.segment.segment import MultiSegment
from capnpy.struct_ import Struct, undefined
from capnpy.enum import enum
from capnpy.printer import print_buffer

def test_undefined():
    assert repr(undefined) == '<undefined>'

def test__as_pointer():
    buf = b('garbage0'
            '\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
            '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
    b1 = Struct.from_buffer(buf, 8, data_size=2, ptrs_size=0)
    p = b1._as_pointer(24) # arbitrary offset
    assert ptr.kind(p) == ptr.STRUCT
    assert ptr.deref(p, 24) == 8
    assert ptr.struct_data_size(p) == 2
    assert ptr.struct_ptrs_size(p) == 0

def test__read_data():
    buf = b('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
            '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
    b1 = Struct.from_buffer(buf, 0, data_size=2, ptrs_size=0)
    assert b1._read_primitive(0, Types.int64.ifmt) == 1
    assert b1._read_primitive(8, Types.int64.ifmt) == 2
    assert b1._read_primitive(16, Types.int64.ifmt) == 0 # outside the buffer

def test__read_struct():
    ## struct Point {
    ##   x @0 :Int64;
    ##   y @1 :Int64;
    ## }
    buf = b('\x00\x00\x00\x00\x02\x00\x00\x00'    # ptr to {x, y}
            '\x01\x00\x00\x00\x00\x00\x00\x00'    # x == 1
            '\x02\x00\x00\x00\x00\x00\x00\x00')   # y == 2
    s = Struct.from_buffer(buf, 0, data_size=0, ptrs_size=1)
    p = s._read_struct(0, Struct)
    assert p._seg is s._seg
    assert p._data_offset == 8
    assert p._data_size == 2
    assert p._ptrs_size == 0
    assert p._read_primitive(0, Types.int64.ifmt) == 1
    assert p._read_primitive(8, Types.int64.ifmt) == 2

def test__read_struct_with_offset():
    ## struct Point {
    ##   x @0 :Int64;
    ##   y @1 :Int64;
    ## }
    buf = b('abcd'                                # garbage
            '\x00\x00\x00\x00\x02\x00\x00\x00'    # ptr to {x, y}
            '\x01\x00\x00\x00\x00\x00\x00\x00'    # x == 1
            '\x02\x00\x00\x00\x00\x00\x00\x00')   # y == 2
    s = Struct.from_buffer(buf, 4, data_size=0, ptrs_size=1)
    p = s._read_struct(0, Struct)
    assert p._seg is s._seg
    assert p._data_offset == 12
    assert p._data_size == 2
    assert p._ptrs_size == 0
    assert p._read_primitive(0, Types.int64.ifmt) == 1
    assert p._read_primitive(8, Types.int64.ifmt) == 2


def test_nested_struct():
    ## struct Rectangle {
    ##   a @0 :Point;
    ##   b @1 :Point;
    ## }
    buf = b('\x04\x00\x00\x00\x02\x00\x00\x00'    # ptr to a
            '\x08\x00\x00\x00\x02\x00\x00\x00'    # ptr to b
            '\x01\x00\x00\x00\x00\x00\x00\x00'    # a.x == 1
            '\x02\x00\x00\x00\x00\x00\x00\x00'    # a.y == 2
            '\x03\x00\x00\x00\x00\x00\x00\x00'    # b.x == 3
            '\x04\x00\x00\x00\x00\x00\x00\x00')   # b.y == 4
    rect = Struct.from_buffer(buf, 0, data_size=0, ptrs_size=2)
    p1 = rect._read_struct(0, Struct)
    p2 = rect._read_struct(8, Struct)
    assert p1._read_primitive(0, Types.int64.ifmt) == 1
    assert p1._read_primitive(8, Types.int64.ifmt) == 2
    assert p2._read_primitive(0, Types.int64.ifmt) == 3
    assert p2._read_primitive(8, Types.int64.ifmt) == 4

def test_null_pointers():
    buf = b'\x00\x00\x00\x00\x00\x00\x00\x00'    # NULL pointer
    blob = Struct.from_buffer(buf, 0, data_size=0, ptrs_size=1)
    assert blob._read_list(0, None, None) is None
    assert blob._read_text_bytes(0) is None
    assert blob._read_struct(0, Struct) is None
    #
    val = b'dummy default value'
    assert blob._read_list(0, None, default_=val) is val
    assert blob._read_text_bytes(0, default_=val) is val


def test_far_pointer_0():
    # test for far pointer with landing_pad==0
    # see also test_list.test_far_pointer_0
    seg0 = b('\x00\x00\x00\x00\x00\x00\x00\x00'    # some garbage
             '\x0a\x00\x00\x00\x01\x00\x00\x00')   # far ptr: pad=0, segment=1, offset=1
    seg1 = b('\x00\x00\x00\x00\x00\x00\x00\x00'    # random data
             '\x00\x00\x00\x00\x02\x00\x00\x00'    # ptr to {x, y}
             '\x01\x00\x00\x00\x00\x00\x00\x00'    # x == 1
             '\x02\x00\x00\x00\x00\x00\x00\x00')   # y == 2
    #
    buf = MultiSegment(seg0+seg1, segment_offsets=(0, 16))
    blob = Struct.from_buffer(buf, 8, data_size=0, ptrs_size=1)
    p = blob._read_struct(0, Struct)
    assert p._read_primitive(0, Types.int64.ifmt) == 1
    assert p._read_primitive(8, Types.int64.ifmt) == 2

def test_far_pointer_1():
    # test for far pointer with landing_pad==0
    # see also test_list.test_far_pointer_1
    seg0 = b('\x00\x00\x00\x00\x00\x00\x00\x00'    # some garbage
             '\x0e\x00\x00\x00\x02\x00\x00\x00')   # far ptr: pad=1, segment=2, offset=1
                                                   # ==> 2nd line of seg2

    seg1 = b('\x00\x00\x00\x00\x00\x00\x00\x00'    # garbage
             '\x01\x00\x00\x00\x00\x00\x00\x00'    # x == 1
             '\x02\x00\x00\x00\x00\x00\x00\x00')   # y == 2

    seg2 = b('\x00\x00\x00\x00\x00\x00\x00\x00'    # garbage
             '\x0a\x00\x00\x00\x01\x00\x00\x00'    # far ptr: pad=0, segment=1, offset=1
                                                   # ==> 2nd line of seg1
             '\x00\x00\x00\x00\x02\x00\x00\x00')   # tag: struct,offset=0,data=2,ptrs=0
    #
    buf = MultiSegment(seg0+seg1+seg2,
                       segment_offsets=(0, len(seg0), len(seg0+seg1)))
    blob = Struct.from_buffer(buf, 8, data_size=0, ptrs_size=1)
    p = blob._read_struct(0, Struct)
    assert p._read_primitive(0, Types.int64.ifmt) == 1
    assert p._read_primitive(8, Types.int64.ifmt) == 2


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
    
    buf = b('\x40\x00\x00\x00\x00\x00\x00\x00'     # area == 64
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
    with pytest.raises(ValueError):
        shape._ensure_union(Shape.__tag__.circle)


def test_compact():
    class Rect(Struct):
        pass

    buf = b('garbage0'
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
    assert buf == b('\x01\x00\x00\x00\x00\x00\x00\x00'    # color == 1
                    '\x04\x00\x00\x00\x02\x00\x00\x00'    # ptr to a
                    '\x00\x00\x00\x00\x00\x00\x00\x00'    # ptr to b, NULL
                    '\x01\x00\x00\x00\x00\x00\x00\x00'    # a.x == 1
                    '\x02\x00\x00\x00\x00\x00\x00\x00')   # a.y == 2

def test_comparisons_fail():
    s = Struct.from_buffer(b'', 0, data_size=0, ptrs_size=0)
    with pytest.raises(TypeError): hash(s)
    with pytest.raises(TypeError): s == s
    with pytest.raises(TypeError): s != s
    with pytest.raises(TypeError): s < s
    with pytest.raises(TypeError): s <= s
    with pytest.raises(TypeError): s > s
    with pytest.raises(TypeError): s >= s

def test_comparisons_succeed():
    class MyStruct(Struct):
        def __hash__(self):
            return 1234

        def _equals(self, other):
            # dummy, random implementation
            return self._seg.buf == other._seg.buf
    #
    s1 = MyStruct.from_buffer(b'', 0, data_size=0, ptrs_size=0)
    s2 = MyStruct.from_buffer(b'', 0, data_size=0, ptrs_size=0)
    s3 = MyStruct.from_buffer(b'x', 0, data_size=0, ptrs_size=0)
    assert hash(s1) == 1234
    assert s1 == s2
    assert s1 != s3
    with pytest.raises(TypeError): s1 < s2
    with pytest.raises(TypeError): s1 <= s2
    with pytest.raises(TypeError): s1 > s2
    with pytest.raises(TypeError): s1 >= s2

def test_can_compare_with_other_types():
    class SubTuple(tuple):
        pass
    s = Struct.from_buffer(b'', 0, data_size=0, ptrs_size=0)
    assert not s == 'hello'
    assert s != 'hello'
    with pytest.raises(TypeError): s == ()
    with pytest.raises(TypeError): s != ()
    with pytest.raises(TypeError): s == SubTuple()
    with pytest.raises(TypeError): s != SubTuple()


def test_check_null_buffer():
    with pytest.raises(AssertionError):
        Struct(None, 0, 0, 0)

def test_raw_dumps_loads():
    buf = b('garbage0'
            '\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
            '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
    obj = Struct.from_buffer(buf, 8, data_size=2, ptrs_size=0)
    mydump = obj._raw_dumps()
    obj2 = Struct._raw_loads(mydump)
    assert obj2._seg.buf == obj._seg.buf
    assert obj2._read_primitive(0, Types.int64.ifmt) == 1
    assert obj2._read_primitive(8, Types.int64.ifmt) == 2

def test_raw_dumps_loads_multi_segment():
    seg0 = b('\x00\x00\x00\x00\x00\x00\x00\x00'    # some garbage
             '\x0a\x00\x00\x00\x01\x00\x00\x00')   # far pointer: segment=1, offset=1
    seg1 = b('\x00\x00\x00\x00\x00\x00\x00\x00'    # random data
             '\x00\x00\x00\x00\x02\x00\x00\x00'    # ptr to {x, y}
             '\x01\x00\x00\x00\x00\x00\x00\x00'    # x == 1
             '\x02\x00\x00\x00\x00\x00\x00\x00')   # y == 2
    #
    buf = MultiSegment(seg0+seg1, segment_offsets=(0, 16))
    obj = Struct.from_buffer(buf, 8, data_size=0, ptrs_size=1)
    #
    mydump = obj._raw_dumps()
    obj2 = Struct._raw_loads(mydump)
    #
    p = obj2._read_struct(0, Struct)
    assert p._read_primitive(0, Types.int64.ifmt) == 1
    assert p._read_primitive(8, Types.int64.ifmt) == 2

def test_unicode_repr():
    class MyStruct(Struct):
        def shortrepr(self):
            return u'hellò'
    s = MyStruct.from_buffer(b'', 0, 0, 0)
    expected = u'<MyStruct: hellò>'
    if not PY3:
        expected = expected.encode('utf-8')
    assert repr(s) == expected
