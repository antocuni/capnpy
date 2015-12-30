import py
from capnpy.struct_ import Struct
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

def test_point_range():
    point = Struct.from_buffer(BUF, 48, None, data_size=2, ptrs_size=0)
    body_start, body_end = point._get_body_range()
    assert body_start == 48
    assert body_end == 64
    #
    extra_start, extra_end = point._get_extra_range()
    assert extra_start == 64
    assert extra_end == 64
    

def test_rect_range():
    rect = Struct.from_buffer(BUF, 8, None, data_size=1, ptrs_size=2)
    body_start, body_end = rect._get_body_range()
    assert body_start == 8
    assert body_end == 32
    #
    extra_start, extra_end = rect._get_extra_range()
    assert extra_start == 48
    assert extra_end == 80

def test_extra_range_one_null_ptrs():
    buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'    # color == 1
           '\x0c\x00\x00\x00\x02\x00\x00\x00'    # ptr to a
           '\x00\x00\x00\x00\x00\x00\x00\x00'    # ptr to b, NULL
           'garbage1'
           'garbage2'
           '\x01\x00\x00\x00\x00\x00\x00\x00'    # a.x == 1
           '\x02\x00\x00\x00\x00\x00\x00\x00')   # a.y == 2
    rect = Struct.from_buffer(buf, 0, None, data_size=1, ptrs_size=2)
    body_start, body_end = rect._get_body_range()
    assert body_start == 0
    assert body_end == 24
    #
    extra_start, extra_end = rect._get_extra_range()
    assert extra_start == 40
    assert extra_end == 56

def test_extra_range_all_null_ptrs():
    buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'    # color == 1
           '\x00\x00\x00\x00\x00\x00\x00\x00'    # ptr to a, NULL
           '\x00\x00\x00\x00\x00\x00\x00\x00')   # ptr to b, NULL
    rect = Struct.from_buffer(buf, 0, None, data_size=1, ptrs_size=2)
    body_start, body_end = rect._get_body_range()
    assert body_start == 0
    assert body_end == 24
    #
    extra_start, extra_end = rect._get_extra_range()
    assert extra_start == 24
    assert extra_end == 24


def test_equality_noptr():
    buf1 = ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
            '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
    buf2 = ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
            '\x03\x00\x00\x00\x00\x00\x00\x00') # 3
    buf3 = 'garbage0' + buf1 + 'garbage1'

    point1 = Struct.from_buffer(buf1, 0, None, data_size=2, ptrs_size=0)
    point2 = Struct.from_buffer(buf2, 0, None, data_size=2, ptrs_size=0)
    point3 = Struct.from_buffer(buf3, 8, None, data_size=2, ptrs_size=0)

    assert not point1 == point2
    assert point1 != point2
    assert point1 == point3
    assert not point1 != point3
    assert hash(point1) == hash(point3) != hash(point2)

def test_equality_ptr():
    john1 = ('\x20\x00\x00\x00\x00\x00\x00\x00'    # age=32
             '\x01\x00\x00\x00\x2a\x00\x00\x00'    # name=ptr
             'J' 'o' 'h' 'n' '\x00\x00\x00\x00')   # John
    
    john2 = ('\x20\x00\x00\x00\x00\x00\x00\x00'    # age=32
             '\x05\x00\x00\x00\x2a\x00\x00\x00'    # name=ptr
            'garbage0'
             'J' 'o' 'h' 'n' '\x00\x00\x00\x00')   # John
    
    paul1 =  ('\x20\x00\x00\x00\x00\x00\x00\x00'   # age=32
              '\x01\x00\x00\x00\x2a\x00\x00\x00'   # name=ptr
              'P' 'a' 'u' 'l' '\x00\x00\x00\x00')  # Paul

    j1 = Struct.from_buffer(john1, 0, None, data_size=1, ptrs_size=1)
    j2 = Struct.from_buffer(john2, 0, None, data_size=1, ptrs_size=1)
    p1 = Struct.from_buffer(paul1, 0, None, data_size=1, ptrs_size=1)
    assert j1 == j2
    assert hash(j1) == hash(j2)
    assert j1 != p1
    assert hash(j1) != hash(p1)


def test_equality_many_ptrs():
    buf1 = ('\x09\x00\x00\x00\x42\x00\x00\x00'    # ptr1
            '\x09\x00\x00\x00\x42\x00\x00\x00'    # ptr2
            '\x09\x00\x00\x00\x82\x00\x00\x00'    # ptr3
            'ABCDEFG\x00'                         # ptr1 == ABCDEFG
            '1234567\x00'                         # ptr2 == 1234567
            '1234567\x00'                         # ptr3 == 1234567\x00ABCDEFG
            'ABCDEFG\x00')

    buf2 = ('\x09\x00\x00\x00\x42\x00\x00\x00'    # ptr1
            '\x09\x00\x00\x00\x82\x00\x00\x00'    # ptr2
            '\x0d\x00\x00\x00\x42\x00\x00\x00'    # ptr3
            'ABCDEFG\x00'                         # ptr1 == ABCDEFG
            '1234567\x00'                         # ptr2 == 1234567\x001234567
            '1234567\x00'
            'ABCDEFG\x00')                        # ptr3 == ABCDEFG

    x = Struct.from_buffer(buf1, 0, None, data_size=0, ptrs_size=3)
    y = Struct.from_buffer(buf2, 0, None, data_size=0, ptrs_size=3)
    
    assert x._read_string(0) == 'ABCDEFG'
    assert x._read_string(8) == '1234567'
    assert x._read_string(16) == '1234567\x00ABCDEFG'

    assert y._read_string(0) == 'ABCDEFG'
    assert y._read_string(8) == '1234567\x001234567'
    assert y._read_string(16) == 'ABCDEFG'

    assert x != y # this is the whole point of the test :)


def test_equality_different_classes():
    class A(Struct):
        pass

    class B(Struct):
        pass

    buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
           '\x02\x00\x00\x00\x00\x00\x00\x00') # 2

    a = A.from_buffer(buf, 0, None, data_size=2, ptrs_size=0)
    b = B.from_buffer(buf, 0, None, data_size=2, ptrs_size=0)
    assert a != b

def test_no_cmp():
    buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
           '\x02\x00\x00\x00\x00\x00\x00\x00') # 2

    p1 = Struct.from_buffer(buf, 0, None, data_size=2, ptrs_size=0)
    p2 = Struct.from_buffer(buf, 0, None, data_size=2, ptrs_size=0)

    py.test.raises(TypeError, "p1 <  p2")
    py.test.raises(TypeError, "p1 <= p2")
    py.test.raises(TypeError, "p1 >  p2")
    py.test.raises(TypeError, "p1 >= p2")


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
    shape = Shape.from_buffer(buf, 0, None, data_size=2, ptrs_size=2)
    assert shape.which() == Shape.__tag__.square
    #
    shape._ensure_union(Shape.__tag__.square)
    py.test.raises(ValueError, "shape._ensure_union(Shape.__tag__.circle)")


def test_split_no_ptrs():
    buf = ('garbage0'
           '\x01\x00\x00\x00\x00\x00\x00\x00'
           '\x02\x00\x00\x00\x00\x00\x00\x00'
           'garbage1')
    p1 = Struct.from_buffer(buf, 8, None, data_size=2, ptrs_size=0)
    body, extra = p1._split(0)
    assert body == ('\x01\x00\x00\x00\x00\x00\x00\x00'
                    '\x02\x00\x00\x00\x00\x00\x00\x00')
    assert extra == ''

def test_split_ptrs():
    buf = ('garbage0'
           '\x01\x00\x00\x00\x00\x00\x00\x00'    # color == 1
           '\x04\x00\x00\x00\x02\x00\x00\x00'    # ptr to a
           '\x00\x00\x00\x00\x00\x00\x00\x00'    # ptr to b, NULL
           '\x01\x00\x00\x00\x00\x00\x00\x00'    # a.x == 1
           '\x02\x00\x00\x00\x00\x00\x00\x00')   # a.y == 2
    rect = Struct.from_buffer(buf, 8, None, data_size=1, ptrs_size=2)
    body, extra = rect._split(2)
    assert body == ('\x01\x00\x00\x00\x00\x00\x00\x00'    # color == 1
                    '\x0c\x00\x00\x00\x02\x00\x00\x00'    # ptr to a
                    '\x00\x00\x00\x00\x00\x00\x00\x00')   # ptr to b, NULL
    #
    assert extra == ('\x01\x00\x00\x00\x00\x00\x00\x00'    # a.x == 1
                     '\x02\x00\x00\x00\x00\x00\x00\x00')   # a.y == 2


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
    rect = Rect.from_buffer(buf, 8, None, data_size=1, ptrs_size=2)
    rect2 = rect.compact()
    assert rect2.__class__ is Rect
    assert rect2._buf == ('\x01\x00\x00\x00\x00\x00\x00\x00'    # color == 1
                          '\x04\x00\x00\x00\x02\x00\x00\x00'    # ptr to a
                          '\x00\x00\x00\x00\x00\x00\x00\x00'    # ptr to b, NULL
                          '\x01\x00\x00\x00\x00\x00\x00\x00'    # a.x == 1
                          '\x02\x00\x00\x00\x00\x00\x00\x00')   # a.y == 2
