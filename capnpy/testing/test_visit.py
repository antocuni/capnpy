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
        assert end == 80
        # XXX: test the equivalent of _get_extra_start, when we implement it

    def test_struct_null_ptr(self):
        buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'    # color == 1
               '\x0c\x00\x00\x00\x02\x00\x00\x00'    # ptr to a
               '\x00\x00\x00\x00\x00\x00\x00\x00'    # ptr to b, NULL
               'garbage1'
               'garbage2'
               '\x01\x00\x00\x00\x00\x00\x00\x00'    # a.x == 1
               '\x02\x00\x00\x00\x00\x00\x00\x00')   # a.y == 2
        end = self.end_of(buf, 0, data_size=1, ptrs_size=2)
        assert end == 56
        # XXX: test _get_extra_start

    def test_struct_all_null_ptrs(self):
        buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'    # color == 1
               '\x00\x00\x00\x00\x00\x00\x00\x00'    # ptr to a, NULL
               '\x00\x00\x00\x00\x00\x00\x00\x00')   # ptr to b, NULL
        end = self.end_of(buf, 0, data_size=1, ptrs_size=2)
        assert end == 24
        # XXX: test _get_extra_start
