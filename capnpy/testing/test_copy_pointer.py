import pytest
from capnpy import ptr
from capnpy.printer import print_buffer
from capnpy.copy_pointer import MutableBuffer, copy_pointer

class TestMutableBuffer(object):

    def test_allocate(self):
        buf = MutableBuffer(16)
        assert buf.allocate(8) == 0
        s = buf.as_string()
        assert s == '\x00' * 8

    def test_allocate_failure(self):
        buf = MutableBuffer(16)
        assert buf.allocate(8) == 0
        assert buf.allocate(8) == 8
        pytest.raises(ValueError, "buf.allocate(1)")

    def test_set_int64(self):
        buf = MutableBuffer(8)
        buf.allocate(8)
        buf.set_int64(0, 0x1234ABCD)
        s = buf.as_string()
        assert s == '\xCD\xAB\x34\x12\x00\x00\x00\x00'

    def test_alloc_struct(self):
        buf = MutableBuffer(64)
        buf.allocate(16)
        a = buf.alloc_struct(0, data_size=3, ptrs_size=0)
        b = buf.alloc_struct(8, data_size=1, ptrs_size=0)
        buf.set_int64(a,    1)
        buf.set_int64(a+8,  2)
        buf.set_int64(a+16, 3)
        buf.set_int64(b,    4)
        s = buf.as_string()
        assert s == ('\x04\x00\x00\x00\x03\x00\x00\x00'   # ptr to a (3, 0)
                     '\x0c\x00\x00\x00\x01\x00\x00\x00'   # ptr to b (1, 0)
                     '\x01\x00\x00\x00\x00\x00\x00\x00'   # a: 1
                     '\x02\x00\x00\x00\x00\x00\x00\x00'   #    2
                     '\x03\x00\x00\x00\x00\x00\x00\x00'   #    3
                     '\x04\x00\x00\x00\x00\x00\x00\x00')  # b: 4


class TestCopyPointer(object):

    def copy_struct(self, src, offset, data_size, ptrs_size):
        dst = MutableBuffer(len(src))
        dst_pos = dst.allocate(8) # allocate the space to store the pointer p
        p = ptr.new_struct(0, data_size, ptrs_size)
        copy_pointer(src, p, offset-8, dst, dst_pos)
        return dst.as_string()

    def test_struct_data(self):
        src = ('garbage0'
               'garbage1'
               '\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
               '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
        dst = self.copy_struct(src, offset=16, data_size=2, ptrs_size=0)
        assert dst == ('\x00\x00\x00\x00\x02\x00\x00\x00'  # ptr (2, 0)
                       '\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
                       '\x02\x00\x00\x00\x00\x00\x00\x00') # 2

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
        src = ('garbage0'
               '\x01\x00\x00\x00\x00\x00\x00\x00'    # color == 1
               '\x0c\x00\x00\x00\x02\x00\x00\x00'    # ptr to a
               '\x10\x00\x00\x00\x02\x00\x00\x00'    # ptr to b
               'garbage1'
               'garbage2'
               '\x01\x00\x00\x00\x00\x00\x00\x00'    # a.x == 1
               '\x02\x00\x00\x00\x00\x00\x00\x00'    # a.y == 2
               '\x03\x00\x00\x00\x00\x00\x00\x00'    # b.x == 3
               '\x04\x00\x00\x00\x00\x00\x00\x00')   # b.y == 4
        dst = self.copy_struct(src, offset=8, data_size=1, ptrs_size=2)
        assert dst == (
            '\x00\x00\x00\x00\x01\x00\x02\x00'       # ptr to Rectangle (1, 2)
            '\x01\x00\x00\x00\x00\x00\x00\x00'       # color == 1
            '\x04\x00\x00\x00\x02\x00\x00\x00'       # ptr to a
            '\x08\x00\x00\x00\x02\x00\x00\x00'       # ptr to b
            '\x01\x00\x00\x00\x00\x00\x00\x00'       # a.x == 1
            '\x02\x00\x00\x00\x00\x00\x00\x00'       # a.y == 2
            '\x03\x00\x00\x00\x00\x00\x00\x00'       # b.x == 3
            '\x04\x00\x00\x00\x00\x00\x00\x00')      # b.y == 4
