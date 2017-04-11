import pytest
import struct
from capnpy.blob import PYX
from capnpy import ptr
from capnpy.printer import print_buffer
from capnpy.segment.segment import Segment
from capnpy.segment.builder import SegmentBuilder
from capnpy.struct_ import Struct
from capnpy.list import PrimitiveItemType, StructItemType, TextItemType
from capnpy.type import Types

class TestSegmentBuilder(object):

    def test_allocate(self):
        buf = SegmentBuilder(16)
        assert buf.allocate(8) == 0
        s = buf.as_string()
        assert s == '\x00' * 8

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

    @pytest.mark.skipif(not PYX, reason='PYX only')
    def test_resize_big_allocation(self):
        buf = SegmentBuilder(32)
        assert buf.length == 32
        assert buf.end == 0
        # make a big allocation, which is bigger than the normal exponential
        # growth of the buffer
        buf.allocate(4096)
        assert buf.length == 4096
        assert buf.end == 4096

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
        buf.write_float32(30, 90)
        buf.write_float64(34, 100)
        s = buf.as_string()
        assert s == expected

    def test_write_generic(self):
        expected = struct.pack('<bBhHiIqQfd', 10, 20, 30, 40, 50, 60, 70, 80, 90, 100)
        n = len(expected)
        buf = SegmentBuilder(n)
        buf.allocate(n)
        buf.write_generic(ord('b'), 0, 10)
        buf.write_generic(ord('B'), 1, 20)
        buf.write_generic(ord('h'), 2, 30)
        buf.write_generic(ord('H'), 4, 40)
        buf.write_generic(ord('i'), 6, 50)
        buf.write_generic(ord('I'), 10, 60)
        buf.write_generic(ord('q'), 14, 70)
        buf.write_generic(ord('Q'), 22, 80)
        buf.write_generic(ord('f'), 30, 90)
        buf.write_generic(ord('d'), 34, 100)
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

    def test_alloc_text_and_data(self):
        buf = SegmentBuilder()
        buf.allocate(32)
        buf.alloc_text(0, 'foo')
        buf.alloc_text(8, None)
        buf.alloc_text(16, 'bar')
        buf.alloc_data(24, 'bar')
        s = buf.as_string()
        print
        print_buffer(s)
        assert s == ('\x0D\x00\x00\x00\x22\x00\x00\x00'    # ptr to 'foo'
                     '\x00\x00\x00\x00\x00\x00\x00\x00'    # NULL
                     '\x09\x00\x00\x00\x22\x00\x00\x00'    # ptr to text 'bar' (4 items)
                     '\x09\x00\x00\x00\x1A\x00\x00\x00'    # ptr to data 'bar' (3 items)
                     'foo\x00\x00\x00\x00\x00'
                     'bar\x00\x00\x00\x00\x00'
                     'bar\x00\x00\x00\x00\x00')

    def test_write_slice(self):
        src = Segment('1234foobar1234')
        buf = SegmentBuilder()
        buf.allocate(8)
        pos = buf.allocate(8)
        buf.write_slice(pos, src, start=4, n=6)
        s = buf.as_string()
        assert s == ('\x00\x00\x00\x00\x00\x00\x00\x00'
                     'foobar\x00\x00')

    def test_null_pointers(self):
        NULL = '\x00\x00\x00\x00\x00\x00\x00\x00' # NULL pointer
        buf = SegmentBuilder()
        pos = buf.allocate(24)
        buf.copy_from_struct(0, Struct, None)
        buf.alloc_text(8, None)
        buf.copy_from_list(16, PrimitiveItemType(Types.int64), None)
        s = buf.as_string()
        assert s == NULL*3

    def test_copy_from_list_int64(self):
        buf = SegmentBuilder()
        buf.allocate(8) # allocate some garbage at the beginning
        pos = buf.allocate(8)
        item_type = PrimitiveItemType(Types.int64)
        buf.copy_from_list(pos, item_type, [1, 2, 3, 4])
        s = buf.as_string()
        assert s == (
            '\x00\x00\x00\x00\x00\x00\x00\x00'   # garbage
            '\x01\x00\x00\x00\x25\x00\x00\x00'   # ptrlist
            '\x01\x00\x00\x00\x00\x00\x00\x00'   # 1
            '\x02\x00\x00\x00\x00\x00\x00\x00'   # 2
            '\x03\x00\x00\x00\x00\x00\x00\x00'   # 3
            '\x04\x00\x00\x00\x00\x00\x00\x00')  # 4

    def test_copy_from_list_int8(self):
        buf = SegmentBuilder()
        buf.allocate(8) # allocate some garbage at the beginning
        pos = buf.allocate(8)
        item_type = PrimitiveItemType(Types.int8)
        buf.copy_from_list(pos, item_type, [1, 2, 3, 4])
        s = buf.as_string()
        assert s == (
            '\x00\x00\x00\x00\x00\x00\x00\x00'   # garbage
            '\x01\x00\x00\x00\x22\x00\x00\x00'   # ptrlist
            '\x01\x02\x03\x04\x00\x00\x00\x00')  # 1,2,3,4 + padding

    def test_copy_from_list_float64(self):
        buf = SegmentBuilder()
        buf.allocate(8) # allocate some garbage at the beginning
        pos = buf.allocate(8)
        item_type = PrimitiveItemType(Types.float64)
        buf.copy_from_list(pos, item_type, [1.234, 2.345, 3.456, 4.567])
        s = buf.as_string()
        assert s == (
            '\x00\x00\x00\x00\x00\x00\x00\x00'   # garbage
            '\x01\x00\x00\x00\x25\x00\x00\x00'   # ptrlist
            '\x58\x39\xb4\xc8\x76\xbe\xf3\x3f'   # 1.234
            '\xc3\xf5\x28\x5c\x8f\xc2\x02\x40'   # 2.345
            '\xd9\xce\xf7\x53\xe3\xa5\x0b\x40'   # 3.456
            '\xf8\x53\xe3\xa5\x9b\x44\x12\x40')  # 4.567

    def test_copy_from_list_of_structs(self):
        class Point(Struct):
            __static_data_size__ = 2
            __static_ptrs_size__ = 0

        buf1 = ('\x0a\x00\x00\x00\x00\x00\x00\x00'    # 10
                '\x64\x00\x00\x00\x00\x00\x00\x00')   # 100
        buf2 = ('\x14\x00\x00\x00\x00\x00\x00\x00'    # 20
                '\xc8\x00\x00\x00\x00\x00\x00\x00')   # 200
        buf3 = ('\x1e\x00\x00\x00\x00\x00\x00\x00'    # 30
                '\x2c\x01\x00\x00\x00\x00\x00\x00')   # 300
        buf4 = ('\x28\x00\x00\x00\x00\x00\x00\x00'    # 40
                '\x90\x01\x00\x00\x00\x00\x00\x00')   # 400
        p1 = Point.from_buffer(buf1, 0, 2, 0)
        p2 = Point.from_buffer(buf2, 0, 2, 0)
        p3 = Point.from_buffer(buf3, 0, 2, 0)
        p4 = Point.from_buffer(buf4, 0, 2, 0)
        #
        buf = SegmentBuilder()
        pos = buf.allocate(8)
        item_type = StructItemType(Point)
        buf.copy_from_list(pos, item_type, [p1, p2, p3, p4])
        s = buf.as_string()
        expected_buf = ('\x01\x00\x00\x00\x47\x00\x00\x00'    # ptrlist
                        '\x10\x00\x00\x00\x02\x00\x00\x00'    # list tag
                        '\x0a\x00\x00\x00\x00\x00\x00\x00'    # 10
                        '\x64\x00\x00\x00\x00\x00\x00\x00'    # 100
                        '\x14\x00\x00\x00\x00\x00\x00\x00'    # 20
                        '\xc8\x00\x00\x00\x00\x00\x00\x00'    # 200
                        '\x1e\x00\x00\x00\x00\x00\x00\x00'    # 30
                        '\x2c\x01\x00\x00\x00\x00\x00\x00'    # 300
                        '\x28\x00\x00\x00\x00\x00\x00\x00'    # 40
                        '\x90\x01\x00\x00\x00\x00\x00\x00')   # 400
        assert s == expected_buf

    def test_copy_from_list_of_text(self):
        buf = SegmentBuilder()
        pos = buf.allocate(8)
        item_type = TextItemType(Types.text)
        buf.copy_from_list(pos, item_type, ['A', 'BC', 'DEF', 'GHIJ'])
        s = buf.as_string()
        expected_buf = ('\x01\x00\x00\x00\x26\x00\x00\x00'   # ptrlist
                        '\x0d\x00\x00\x00\x12\x00\x00\x00'   # ptr item 1
                        '\x0d\x00\x00\x00\x1a\x00\x00\x00'   # ptr item 2
                        '\x0d\x00\x00\x00\x22\x00\x00\x00'   # ptr item 3
                        '\x0d\x00\x00\x00\x2a\x00\x00\x00'   # ptr item 4
                        'A' '\x00\x00\x00\x00\x00\x00\x00'   # A
                        'B' 'C' '\x00\x00\x00\x00\x00\x00'   # BC
                        'D' 'E' 'F' '\x00\x00\x00\x00\x00'   # DEF
                        'G' 'H' 'I' 'J' '\x00\x00\x00\x00')  # GHIJ
        assert s == expected_buf


    def test_copy_from_list_of_structs_with_pointers(self):
        class Person(Struct):
            __static_data_size__ = 1
            __static_ptrs_size__ = 1

        john =  ('\x20\x00\x00\x00\x00\x00\x00\x00'    # age=32
                 '\x01\x00\x00\x00\x2a\x00\x00\x00'    # name=ptr
                 'J' 'o' 'h' 'n' '\x00\x00\x00\x00')   # John

        # emily is a "split struct", with garbage between the body and the extra
        emily = ('garbage0'
                 '\x18\x00\x00\x00\x00\x00\x00\x00'    # age=24
                 '\x09\x00\x00\x00\x32\x00\x00\x00'    # name=ptr
                 'garbage1'
                 'garbage2'
                 '\x45\x6d\x69\x6c\x79\x00\x00\x00'    # Emily
                 'garbage3')

        john = Person.from_buffer(john, 0, 1, 1)
        emily = Person.from_buffer(emily, 8, 1, 1)
        #
        buf = SegmentBuilder()
        pos = buf.allocate(8)
        item_type = StructItemType(Person)
        buf.copy_from_list(pos, item_type, [john, emily])
        s = buf.as_string()
        expected_buf = ('\x01\x00\x00\x00\x27\x00\x00\x00'    # ptrlist
                        '\x08\x00\x00\x00\x01\x00\x01\x00'    # list tag
                        '\x20\x00\x00\x00\x00\x00\x00\x00'    # age=32
                        '\x09\x00\x00\x00\x2a\x00\x00\x00'    # name=ptr
                        '\x18\x00\x00\x00\x00\x00\x00\x00'    # age=24
                        '\x05\x00\x00\x00\x32\x00\x00\x00'    # name=ptr
                        'J' 'o' 'h' 'n' '\x00\x00\x00\x00'    # John
                        'E' 'm' 'i' 'l' 'y' '\x00\x00\x00')   # Emily
        assert s == expected_buf
