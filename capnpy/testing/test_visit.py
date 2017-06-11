from capnpy import ptr
from capnpy.printer import print_buffer
from capnpy.visit import end_of
from capnpy.segment.segment import Segment

class TestEndOf(object):

    def end_of(self, buf, offset, data_size, ptrs_size):
        buf = Segment(buf)
        p = ptr.new_struct(0, data_size, ptrs_size)
        return end_of(buf, p, offset-8)

    def test_struct_data(self):
        buf = ('garbage0'
               'garbage1'
               '\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
               '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
        end = self.end_of(buf, 16, data_size=2, ptrs_size=0)
        assert end == 32

    def test_struct_ptrs_compact(self):
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
        buf = ('garbage0'
               '\x01\x00\x00\x00\x00\x00\x00\x00'    # color == 1
               '\x04\x00\x00\x00\x02\x00\x00\x00'    # ptr to a
               '\x08\x00\x00\x00\x02\x00\x00\x00'    # ptr to b
               '\x01\x00\x00\x00\x00\x00\x00\x00'    # a.x == 1
               '\x02\x00\x00\x00\x00\x00\x00\x00'    # a.y == 2
               '\x03\x00\x00\x00\x00\x00\x00\x00'    # b.x == 3
               '\x04\x00\x00\x00\x00\x00\x00\x00')   # b.y == 4
        end = self.end_of(buf, 8, data_size=1, ptrs_size=2)
        assert end == 64

    def test_struct_gap_before_children(self):
        buf = ('garbage0'
               '\x01\x00\x00\x00\x00\x00\x00\x00'    # color == 1
               '\x0c\x00\x00\x00\x02\x00\x00\x00'    # ptr to a
               '\x10\x00\x00\x00\x02\x00\x00\x00'    # ptr to b
               'garbage1'
               'garbage2'
               '\x01\x00\x00\x00\x00\x00\x00\x00'    # a.x == 1
               '\x02\x00\x00\x00\x00\x00\x00\x00'    # a.y == 2
               '\x03\x00\x00\x00\x00\x00\x00\x00'    # b.x == 3
               '\x04\x00\x00\x00\x00\x00\x00\x00')   # b.y == 4
        end = self.end_of(buf, 8, data_size=1, ptrs_size=2)
        assert end == -1 # not compact

    def test_struct_gap_between_children(self):
        buf = ('garbage0'
               '\x01\x00\x00\x00\x00\x00\x00\x00'    # color == 1
               '\x04\x00\x00\x00\x02\x00\x00\x00'    # ptr to a
               '\x0c\x00\x00\x00\x02\x00\x00\x00'    # ptr to b
               '\x01\x00\x00\x00\x00\x00\x00\x00'    # a.x == 1
               '\x02\x00\x00\x00\x00\x00\x00\x00'    # a.y == 2
               'garbage1'
               '\x03\x00\x00\x00\x00\x00\x00\x00'    # b.x == 3
               '\x04\x00\x00\x00\x00\x00\x00\x00')   # b.y == 4
        end = self.end_of(buf, 8, data_size=1, ptrs_size=2)
        assert end == -1 # not compact

    def test_struct_first_null_ptr(self):
        buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'    # color == 1
               '\x04\x00\x00\x00\x02\x00\x00\x00'    # ptr to a
               '\x00\x00\x00\x00\x00\x00\x00\x00'    # ptr to b, NULL
               '\x01\x00\x00\x00\x00\x00\x00\x00'    # a.x == 1
               '\x02\x00\x00\x00\x00\x00\x00\x00')   # a.y == 2
        end = self.end_of(buf, 0, data_size=1, ptrs_size=2)
        assert end == 40

    def test_struct_second_null_ptr(self):
        buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'    # color == 1
               '\x00\x00\x00\x00\x00\x00\x00\x00'    # ptr to a, NULL
               '\x00\x00\x00\x00\x02\x00\x00\x00'    # ptr to b
               '\x01\x00\x00\x00\x00\x00\x00\x00'    # a.x == 1
               '\x02\x00\x00\x00\x00\x00\x00\x00')   # a.y == 2
        end = self.end_of(buf, 0, data_size=1, ptrs_size=2)
        assert end == 40

    def test_struct_all_null_ptrs(self):
        buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'    # color == 1
               '\x00\x00\x00\x00\x00\x00\x00\x00'    # ptr to a, NULL
               '\x00\x00\x00\x00\x00\x00\x00\x00')   # ptr to b, NULL
        end = self.end_of(buf, 0, data_size=1, ptrs_size=2)
        assert end == 24

    def test_children_out_of_order(self):
        buf = ('garbage0'
               '\x01\x00\x00\x00\x00\x00\x00\x00'    # color == 1
               '\x0c\x00\x00\x00\x02\x00\x00\x00'    # ptr to a
               '\x00\x00\x00\x00\x02\x00\x00\x00'    # ptr to b
               '\x01\x00\x00\x00\x00\x00\x00\x00'    # b.x == 1
               '\x02\x00\x00\x00\x00\x00\x00\x00'    # b.y == 2
               '\x03\x00\x00\x00\x00\x00\x00\x00'    # a.x == 3
               '\x04\x00\x00\x00\x00\x00\x00\x00')   # a.y == 4
        end = self.end_of(buf, 8, data_size=1, ptrs_size=2)
        assert end == -1

    def test_list_primitive(self):
        buf = ('\x01\x00\x00\x00\x1a\x00\x00\x00'   #  0: ptr list<8>  to a
               '\x01\x02\x03\x00\x00\x00\x00\x00'   #  8: a = [1, 2, 3]
               #
               '\x01\x00\x00\x00\x1b\x00\x00\x00'   # 16: ptr list<16> to b
               '\x04\x00\x05\x00\x06\x00\x00\x00'   # 24: b = [4, 5, 6]
               #
               '\x01\x00\x00\x00\x1c\x00\x00\x00'   # 32: ptr list<32> to c
               '\x07\x00\x00\x00\x08\x00\x00\x00'   # 40: c = [7, 8, 9]
               '\x09\x00\x00\x00\x00\x00\x00\x00'   # 48:
               #
               '\x01\x00\x00\x00\x1d\x00\x00\x00'   # 56: ptr list<64> to d
               '\x0a\x00\x00\x00\x00\x00\x00\x00'   # 64: d = [10, 11, 12]
               '\x0b\x00\x00\x00\x00\x00\x00\x00'   # 72
               '\x0c\x00\x00\x00\x00\x00\x00\x00')  # 80
        #
        end_a = self.end_of(buf, 0, data_size=0, ptrs_size=1)
        end_b = self.end_of(buf, 16, data_size=0, ptrs_size=1)
        end_c = self.end_of(buf, 32, data_size=0, ptrs_size=1)
        end_d = self.end_of(buf, 56, data_size=0, ptrs_size=1)
        assert end_a == 16 # 8 + 3      rounded to word boundary
        assert end_b == 32 # 24 + (3*2) rounded to word boundary
        assert end_c == 56 # 40 + (3*4) rounded to word boundary
        assert end_d == 88 # 64 + (3*8) rounded to word boundary

    def test_list_of_bool(self):
        buf = ('garbage1'
               '\x01\x00\x00\x00\x19\x00\x00\x00'    # ptrlist
               '\x03\x00\x00\x00\x00\x00\x00\x00')   # [True, True, False]
        end = self.end_of(buf, 8, data_size=0, ptrs_size=1)
        assert end == 24

    def test_list_composite_compact(self):
        ## struct Point {
        ##   x @0 :Int64;
        ##   y @1 :Int64;
        ##   name @2 :Text;
        ## }
        buf = ('garbage0'
               '\x01\x00\x00\x00\x4f\x00\x00\x00'   # ptr to list
               '\x0c\x00\x00\x00\x02\x00\x01\x00'   # list tag
               '\x01\x00\x00\x00\x00\x00\x00\x00'   # points[0].x == 1
               '\x02\x00\x00\x00\x00\x00\x00\x00'   # points[0].y == 2
               '\x19\x00\x00\x00\x42\x00\x00\x00'   # points[0].name == ptr
               '\x03\x00\x00\x00\x00\x00\x00\x00'   # points[1].x == 3
               '\x04\x00\x00\x00\x00\x00\x00\x00'   # points[1].y == 4
               '\x11\x00\x00\x00\x42\x00\x00\x00'   # points[1].name == ptr
               '\x05\x00\x00\x00\x00\x00\x00\x00'   # points[2].x == 5
               '\x06\x00\x00\x00\x00\x00\x00\x00'   # points[2].y == 6
               '\x09\x00\x00\x00\x42\x00\x00\x00'   # points[2].name == ptr
               'P' 'o' 'i' 'n' 't' ' ' 'A' '\x00'
               'P' 'o' 'i' 'n' 't' ' ' 'B' '\x00'
               'P' 'o' 'i' 'n' 't' ' ' 'C' '\x00'
               'garbage1')
        end = self.end_of(buf, 8, data_size=0, ptrs_size=1)
        assert end == 120
        assert buf[end:] == 'garbage1'

    def test_list_composite_not_compact(self):
        ## struct Point {
        ##   x @0 :Int64;
        ##   y @1 :Int64;
        ##   name @2 :Text;
        ## }
        buf = ('garbage0'
               '\x01\x00\x00\x00\x4f\x00\x00\x00'   # ptr to list
               '\x0c\x00\x00\x00\x02\x00\x01\x00'   # list tag
               '\x01\x00\x00\x00\x00\x00\x00\x00'   # points[0].x == 1
               '\x02\x00\x00\x00\x00\x00\x00\x00'   # points[0].y == 2
               '\x1d\x00\x00\x00\x42\x00\x00\x00'   # points[0].name == ptr
               '\x03\x00\x00\x00\x00\x00\x00\x00'   # points[1].x == 3
               '\x04\x00\x00\x00\x00\x00\x00\x00'   # points[1].y == 4
               '\x15\x00\x00\x00\x42\x00\x00\x00'   # points[1].name == ptr
               '\x05\x00\x00\x00\x00\x00\x00\x00'   # points[2].x == 5
               '\x06\x00\x00\x00\x00\x00\x00\x00'   # points[2].y == 6
               '\x0d\x00\x00\x00\x42\x00\x00\x00'   # points[2].name == ptr
               'garbage1'
               'P' 'o' 'i' 'n' 't' ' ' 'A' '\x00'
               'P' 'o' 'i' 'n' 't' ' ' 'B' '\x00'
               'P' 'o' 'i' 'n' 't' ' ' 'C' '\x00'
               'garbage2')
        end = self.end_of(buf, 8, data_size=0, ptrs_size=1)
        assert end == -1 # not compact

    def test_list_composite_one_null_ptr(self):
        ## struct Point {
        ##   x @0 :Int64;
        ##   y @1 :Int64;
        ##   name @2 :Text;
        ## }
        buf = ('garbage0'
               '\x01\x00\x00\x00\x4f\x00\x00\x00'   # ptr to list
               '\x0c\x00\x00\x00\x02\x00\x01\x00'   # list tag
               '\x01\x00\x00\x00\x00\x00\x00\x00'   # points[0].x == 1
               '\x02\x00\x00\x00\x00\x00\x00\x00'   # points[0].y == 2
               '\x19\x00\x00\x00\x42\x00\x00\x00'   # points[0].name == ptr
               '\x03\x00\x00\x00\x00\x00\x00\x00'   # points[1].x == 3
               '\x04\x00\x00\x00\x00\x00\x00\x00'   # points[1].y == 4
               '\x11\x00\x00\x00\x42\x00\x00\x00'   # points[1].name == ptr
               '\x05\x00\x00\x00\x00\x00\x00\x00'   # points[2].x == 5
               '\x06\x00\x00\x00\x00\x00\x00\x00'   # points[2].y == 6
               '\x00\x00\x00\x00\x00\x00\x00\x00'   # points[2].name == NULL
               'P' 'o' 'i' 'n' 't' ' ' 'A' '\x00'
               'P' 'o' 'i' 'n' 't' ' ' 'B' '\x00'
               'garbage1')
        end = self.end_of(buf, 8, data_size=0, ptrs_size=1)
        assert end == 112
        assert buf[end:] == 'garbage1'

    def test_list_composite_all_null_ptrs(self):
        ## struct Point {
        ##   x @0 :Int64;
        ##   y @1 :Int64;
        ##   name @2 :Text;
        ## }
        buf = ('garbage0'
               '\x01\x00\x00\x00\x4f\x00\x00\x00'   # ptr to list
               '\x0c\x00\x00\x00\x02\x00\x01\x00'   # list tag
               '\x01\x00\x00\x00\x00\x00\x00\x00'   # points[0].x == 1
               '\x02\x00\x00\x00\x00\x00\x00\x00'   # points[0].y == 2
               '\x00\x00\x00\x00\x00\x00\x00\x00'   # points[0].name == NULL
               '\x03\x00\x00\x00\x00\x00\x00\x00'   # points[1].x == 3
               '\x04\x00\x00\x00\x00\x00\x00\x00'   # points[1].y == 4
               '\x00\x00\x00\x00\x00\x00\x00\x00'   # points[1].name == NULL
               '\x05\x00\x00\x00\x00\x00\x00\x00'   # points[2].x == 5
               '\x06\x00\x00\x00\x00\x00\x00\x00'   # points[2].y == 6
               '\x00\x00\x00\x00\x00\x00\x00\x00'   # points[2].name == NULL
               'garbage1')
        end = self.end_of(buf, 8, data_size=0, ptrs_size=1)
        assert end == 96
        assert buf[end:] == 'garbage1'

    def test_list_composite_no_ptr(self):
        buf = ('garbage0'
               '\x01\x00\x00\x00\x27\x00\x00\x00'   # ptr to list
               '\x08\x00\x00\x00\x02\x00\x00\x00'   # list tag
               '\x01\x00\x00\x00\x00\x00\x00\x00'   # p[0].x == 1
               '\x02\x00\x00\x00\x00\x00\x00\x00'   # p[0].y == 2
               '\x03\x00\x00\x00\x00\x00\x00\x00'   # p[1].x == 3
               '\x04\x00\x00\x00\x00\x00\x00\x00'   # p[1].y == 4
               'garbage1'
               'garbage2')
        end = self.end_of(buf, 8, data_size=0, ptrs_size=1)
        assert end == 56
        assert buf[end:] == 'garbage1garbage2'

    def test_list_of_pointers_compact(self):
        buf = ('garbage0'
               '\x01\x00\x00\x00\x1e\x00\x00\x00'   # ptr to list
               '\x09\x00\x00\x00\x32\x00\x00\x00'   # strings[0] == ptr to #0
               '\x09\x00\x00\x00\x52\x00\x00\x00'   # strings[1] == ptr to #1
               '\x0d\x00\x00\x00\xb2\x00\x00\x00'   # strings[2] == ptr to #2
               'h' 'e' 'l' 'l' 'o' '\x00\x00\x00'   # #0
               'c' 'a' 'p' 'n' 'p' 'r' 'o' 't'      # #1...
               'o' '\x00\x00\x00\x00\x00\x00\x00'
               't' 'h' 'i' 's' ' ' 'i' 's' ' '      # #2...
               'a' ' ' 'l' 'o' 'n' 'g' ' ' 's'
               't' 'r' 'i' 'n' 'g' '\x00\x00\x00')
        end = self.end_of(buf, 8, data_size=0, ptrs_size=1)
        assert end == 88

    def test_list_of_pointers_not_compact(self):
        buf = ('garbage0'
               '\x01\x00\x00\x00\x1e\x00\x00\x00'   # ptr to list
               '\x0d\x00\x00\x00\x32\x00\x00\x00'   # strings[0] == ptr to #0
               '\x0d\x00\x00\x00\x52\x00\x00\x00'   # strings[1] == ptr to #1
               '\x11\x00\x00\x00\xb2\x00\x00\x00'   # strings[2] == ptr to #2
               'garbage1'
               'h' 'e' 'l' 'l' 'o' '\x00\x00\x00'   # #0
               'c' 'a' 'p' 'n' 'p' 'r' 'o' 't'      # #1...
               'o' '\x00\x00\x00\x00\x00\x00\x00'
               't' 'h' 'i' 's' ' ' 'i' 's' ' '      # #2...
               'a' ' ' 'l' 'o' 'n' 'g' ' ' 's'
               't' 'r' 'i' 'n' 'g' '\x00\x00\x00')
        end = self.end_of(buf, 8, data_size=0, ptrs_size=1)
        assert end == -1 # not compact

    def test_list_of_pointers_all_null(self):
        buf = ('garbage0'
               '\x01\x00\x00\x00\x1e\x00\x00\x00'   # ptr to list
               '\x00\x00\x00\x00\x00\x00\x00\x00'
               '\x00\x00\x00\x00\x00\x00\x00\x00'
               '\x00\x00\x00\x00\x00\x00\x00\x00'
               'garbage1')
        end = self.end_of(buf, 8, data_size=0, ptrs_size=1)
        assert end == 40
        assert buf[end:] == 'garbage1'
