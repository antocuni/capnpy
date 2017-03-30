import pytest
import struct
from capnpy import ptr
from capnpy.printer import print_buffer
from capnpy.segment.builder import SegmentBuilder

WIP = pytest.mark.skipif(getattr(SegmentBuilder, 'WIP', False), reason='WIP')

class TestSegmentBuilder(object):

    def test_allocate(self):
        buf = SegmentBuilder(16)
        assert buf.allocate(8) == 0
        s = buf.as_string()
        assert s == '\x00' * 8

    def test_write(self):
        expected = struct.pack('<bBhHiIqQfd', 10, 20, 30, 40, 50, 60, 70, 80, 90, 100)
        n = len(expected)
        buf = SegmentBuilder(n)
        buf.allocate(n)
        buf.write_int8(0, 10)
        buf.write_uint8(1, 20)
        buf.write_int16(2, 30)
        buf.write_uint16(4, 40)
        buf.write_int32(6, 50)
        buf.write_uint32(10, 60)
        buf.write_int64(14, 70)
        buf.write_uint64(22, 80)
        buf.write_float(30, 90)
        buf.write_double(34, 100)
        s = buf.as_string()
        assert s == expected

    def test_alloc_struct(self):
        buf = SegmentBuilder(64)
        buf.allocate(16)
        a = buf.alloc_struct(0, data_size=3, ptrs_size=0)
        b = buf.alloc_struct(8, data_size=1, ptrs_size=0)
        buf.write_int64(a,    1)
        buf.write_int64(a+8,  2)
        buf.write_int64(a+16, 3)
        buf.write_int64(b,    4)
        s = buf.as_string()
        assert s == ('\x04\x00\x00\x00\x03\x00\x00\x00'   # ptr to a (3, 0)
                     '\x0c\x00\x00\x00\x01\x00\x00\x00'   # ptr to b (1, 0)
                     '\x01\x00\x00\x00\x00\x00\x00\x00'   # a: 1
                     '\x02\x00\x00\x00\x00\x00\x00\x00'   #    2
                     '\x03\x00\x00\x00\x00\x00\x00\x00'   #    3
                     '\x04\x00\x00\x00\x00\x00\x00\x00')  # b: 4

    def test_alloc_list(self):
        buf = SegmentBuilder(64)
        buf.allocate(16)
        a = buf.alloc_list(0, size_tag=ptr.LIST_SIZE_8, item_count=4, body_length=4)
        b = buf.alloc_list(8, size_tag=ptr.LIST_SIZE_16, item_count=2, body_length=4)
        buf.write_int8(a,   ord('f'))
        buf.write_int8(a+1, ord('o'))
        buf.write_int8(a+2, ord('o'))
        buf.write_int8(a+3, ord('\x00'))
        #
        buf.write_int16(b,   0x1234)
        buf.write_int16(b+2, 0x5678)
        #
        s = buf.as_string()
        assert s == ('\x05\x00\x00\x00\x22\x00\x00\x00'    # ptrlist int8, item_count=4
                     '\x05\x00\x00\x00\x13\x00\x00\x00'    # ptrlist int16, item_count=2
                     'foo\x00\x00\x00\x00\x00'
                     '\x34\x12\x78\x56\x00\x00\x00\x00')   # 0x1234 0x5678

    def test_resize(self):
        buf = SegmentBuilder()
        buf.allocate(64)
        print
        buf.write_int64(0, 42)
        for i in range(63):
            buf.allocate(64)
        s = buf.as_string()
        assert len(s) == 64*64
        assert s[:8] == struct.pack('q', 42)
        assert s[8:] == '\x00' * (64*64-8)

    @WIP
    def test_resize_big_allocation(self):
        buf = SegmentBuilder(32)
        assert buf.length == 32
        assert buf.end == 0
        # make a big allocation, which is bigger than the normal exponential
        # growth of the buffer
        buf.allocate(4096)
        assert buf.length == 4096
        assert buf.end == 4096

