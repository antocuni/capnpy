from capnpy.struct_ import GenericStruct

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
    point = GenericStruct.from_buffer_and_size(BUF, 48, data_size=2, ptrs_size=0)
    body_start, body_end = point._get_body_range()
    assert body_start == 48
    assert body_end == 64
    #
    extra_start, extra_end = point._get_extra_range()
    assert extra_start == 64
    assert extra_end == 64
    

def test_rect_range():
    rect = GenericStruct.from_buffer_and_size(BUF, 8, data_size=1, ptrs_size=2)
    body_start, body_end = rect._get_body_range()
    assert body_start == 8
    assert body_end == 32
    #
    extra_start, extra_end = rect._get_extra_range()
    assert extra_start == 48
    assert extra_end == 80


def test_equality_noptr():
    buf1 = ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
            '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
    buf2 = ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
            '\x03\x00\x00\x00\x00\x00\x00\x00') # 3
    buf3 = 'garbage0' + buf1 + 'garbage1'

    point1 = GenericStruct.from_buffer_and_size(buf1, 0, data_size=2, ptrs_size=0)
    point2 = GenericStruct.from_buffer_and_size(buf2, 0, data_size=2, ptrs_size=0)
    point3 = GenericStruct.from_buffer_and_size(buf3, 8, data_size=2, ptrs_size=0)

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

    j1 = GenericStruct.from_buffer_and_size(john1, 0, data_size=1, ptrs_size=1)
    j2 = GenericStruct.from_buffer_and_size(john2, 0, data_size=1, ptrs_size=1)
    p1 = GenericStruct.from_buffer_and_size(paul1, 0, data_size=1, ptrs_size=1)
    assert j1 == j2
    assert hash(j1) == hash(j2)
    assert j1 != p1
    assert hash(j1) != hash(p1)
