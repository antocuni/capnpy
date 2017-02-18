from capnpy import ptr
from capnpy.visit import end_of
from capnpy.blob import CapnpBuffer

class TestEndOf(object):

    def end_of(self, buf, offset, data_size, ptrs_size):
        buf = CapnpBuffer(buf)
        p = ptr.new_struct(0, data_size, ptrs_size)
        return end_of(buf, p, offset-8)

    def test_struct_data(self):
        buf = ('garbage0'
               'garbage1'
               '\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
               '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
        end = self.end_of(buf, 16, data_size=2, ptrs_size=0)
        assert end == 32

    def test_struct_ptrs(self):
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
               '\x0c\x00\x00\x00\x02\x00\x00\x00'    # ptr to a
               '\x10\x00\x00\x00\x02\x00\x00\x00'    # ptr to b
               'garbage1'
               'garbage2'
               '\x01\x00\x00\x00\x00\x00\x00\x00'    # a.x == 1
               '\x02\x00\x00\x00\x00\x00\x00\x00'    # a.y == 2
               '\x03\x00\x00\x00\x00\x00\x00\x00'    # b.x == 3
               '\x04\x00\x00\x00\x00\x00\x00\x00')   # b.y == 4
        end = self.end_of(buf, 8, data_size=1, ptrs_size=2)
        #assert start == 48
        assert end == 80

    def test_struct_null_ptr(self):
        buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'    # color == 1
               '\x0c\x00\x00\x00\x02\x00\x00\x00'    # ptr to a
               '\x00\x00\x00\x00\x00\x00\x00\x00'    # ptr to b, NULL
               'garbage1'
               'garbage2'
               '\x01\x00\x00\x00\x00\x00\x00\x00'    # a.x == 1
               '\x02\x00\x00\x00\x00\x00\x00\x00')   # a.y == 2
        end = self.end_of(buf, 0, data_size=1, ptrs_size=2)
        #assert start == 40  # XXX
        assert end == 56

    def test_struct_all_null_ptrs(self):
        buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'    # color == 1
               '\x00\x00\x00\x00\x00\x00\x00\x00'    # ptr to a, NULL
               '\x00\x00\x00\x00\x00\x00\x00\x00')   # ptr to b, NULL
        end = self.end_of(buf, 0, data_size=1, ptrs_size=2)
        #assert start == 24 # XXX
        assert end == 24

    def test_list_primitive(self):
        buf = ('\x0d\x00\x00\x00\x1a\x00\x00\x00'   #  0: ptr list<8>  to a
               '\x0d\x00\x00\x00\x1b\x00\x00\x00'   #  8: ptr list<16> to b
               '\x0d\x00\x00\x00\x1c\x00\x00\x00'   # 16: ptr list<32> to c
               '\x11\x00\x00\x00\x1d\x00\x00\x00'   # 24: ptr list<64> to d
               '\x01\x02\x03\x00\x00\x00\x00\x00'   # 32: a = [1, 2, 3]
               '\x04\x00\x05\x00\x06\x00\x00\x00'   # 40: b = [4, 5, 6]
               '\x07\x00\x00\x00\x08\x00\x00\x00'   # 48: c = [7, 8, 9]
               '\x09\x00\x00\x00\x00\x00\x00\x00'   # 56:
               '\x0a\x00\x00\x00\x00\x00\x00\x00'   # 64: d = [10, 11, 12]
               '\x0b\x00\x00\x00\x00\x00\x00\x00'   # 72
               '\x0c\x00\x00\x00\x00\x00\x00\x00')  # 80

        end_a = self.end_of(buf, 0, data_size=0, ptrs_size=1)
        end_b = self.end_of(buf, 8, data_size=0, ptrs_size=1)
        end_c = self.end_of(buf, 16, data_size=0, ptrs_size=1)
        end_d = self.end_of(buf, 24, data_size=0, ptrs_size=1)
        #assert body_start == ??? # XXX
        assert end_a == 32 + 3
        assert end_b == 40 + (3*2)
        assert end_c == 48 + (3*4)
        assert end_d == 64 + (3*8)
