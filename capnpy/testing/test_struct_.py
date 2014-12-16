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
