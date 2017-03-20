import pytest
from capnpy.printer import print_buffer
from capnpy.copy_pointer import MutableBuffer

class TestMutableBuffer(object):

    def test_allocate(self):
        buf = MutableBuffer(16)
        assert buf.allocate(8) == 0
        s = buf.as_bytes()
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
        s = buf.as_bytes()
        assert s == '\xCD\xAB\x34\x12\x00\x00\x00\x00'

    def test_new_struct(self):
        buf = MutableBuffer(64)
        buf.allocate(16)
        a = buf.new_struct(0, data_size=3, ptrs_size=0)
        b = buf.new_struct(8, data_size=1, ptrs_size=0)
        buf.set_int64(a,    1)
        buf.set_int64(a+8,  2)
        buf.set_int64(a+16, 3)
        buf.set_int64(b,    4)
        s = buf.as_bytes()
        assert s == ('\x04\x00\x00\x00\x03\x00\x00\x00'   # ptr to a (3, 0)
                     '\x0c\x00\x00\x00\x01\x00\x00\x00'   # ptr to b (1, 0)
                     '\x01\x00\x00\x00\x00\x00\x00\x00'   # a: 1
                     '\x02\x00\x00\x00\x00\x00\x00\x00'   #    2
                     '\x03\x00\x00\x00\x00\x00\x00\x00'   #    3
                     '\x04\x00\x00\x00\x00\x00\x00\x00')  # b: 4
