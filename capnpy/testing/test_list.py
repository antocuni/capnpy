# -*- encoding: utf-8 -*-

import py
import pytest
import six
from six import b

from capnpy.printer import print_buffer
from capnpy.type import Types
from capnpy.segment.segment import MultiSegment
from capnpy import ptr
from capnpy.list import (List, ItemType, VoidItemType, BoolItemType,
                         StructItemType, PrimitiveItemType, TextItemType,
                         ListItemType, TextUnicodeItemType, EnumItemType)
from capnpy.struct_ import Struct

def test_read_list():
    buf = b('\x01\x00\x00\x00\x25\x00\x00\x00'   # ptrlist
           '\x01\x00\x00\x00\x00\x00\x00\x00'   # 1
           '\x02\x00\x00\x00\x00\x00\x00\x00'   # 2
           '\x03\x00\x00\x00\x00\x00\x00\x00'   # 3
           '\x04\x00\x00\x00\x00\x00\x00\x00')  # 4
    blob = Struct.from_buffer(buf, 0, data_size=0, ptrs_size=1)
    lst = blob._read_list(0, PrimitiveItemType(Types.int64))
    assert lst._seg is blob._seg
    assert lst._offset == 8
    assert lst._item_offset == 0
    assert lst._item_count == 4
    assert lst._item_length == 8
    assert lst._getitem_fast(0) == 1
    assert lst._getitem_fast(1) == 2
    assert lst._getitem_fast(2) == 3
    assert lst._getitem_fast(3) == 4

def test_read_list_offset():
    buf = b('abcd'                               # random garbage
           '\x01\x00\x00\x00\x25\x00\x00\x00'   # ptrlist
           '\x01\x00\x00\x00\x00\x00\x00\x00'   # 1
           '\x02\x00\x00\x00\x00\x00\x00\x00'   # 2
           '\x03\x00\x00\x00\x00\x00\x00\x00'   # 3
           '\x04\x00\x00\x00\x00\x00\x00\x00')  # 4
    blob = Struct.from_buffer(buf, 4, data_size=0, ptrs_size=1)
    lst = blob._read_list(0, PrimitiveItemType(Types.int64))
    assert lst._seg is blob._seg
    assert lst._offset == 12
    assert lst._item_count == 4
    assert lst._item_length == 8
    assert lst._getitem_fast(0) == 1
    assert lst._getitem_fast(1) == 2
    assert lst._getitem_fast(2) == 3
    assert lst._getitem_fast(3) == 4

def test_list_of_structs():
    class Point(Struct):
        __static_data_size__ = 2
        __static_ptrs_size__ = 0

    # list of Point {x: Int64, y: Int64}
    buf = b('\x01\x00\x00\x00\x47\x00\x00\x00'    # ptrlist
           '\x10\x00\x00\x00\x02\x00\x00\x00'    # list tag
           '\x0a\x00\x00\x00\x00\x00\x00\x00'    # 10
           '\x64\x00\x00\x00\x00\x00\x00\x00'    # 100
           '\x14\x00\x00\x00\x00\x00\x00\x00'    # 20
           '\xc8\x00\x00\x00\x00\x00\x00\x00'    # 200
           '\x1e\x00\x00\x00\x00\x00\x00\x00'    # 30
           '\x2c\x01\x00\x00\x00\x00\x00\x00'    # 300
           '\x28\x00\x00\x00\x00\x00\x00\x00'    # 40
           '\x90\x01\x00\x00\x00\x00\x00\x00')   # 400
    blob = Struct.from_buffer(buf, 0, data_size=0, ptrs_size=1)
    lst = blob._read_list(0, StructItemType(Point))
    assert lst._seg is blob._seg
    assert lst._offset == 8
    assert lst._item_offset == 8
    assert lst._item_count == 4
    assert lst._item_length == 16
    #
    assert len(lst) == 4
    def read_point(i):
        p = lst[i]
        assert p._data_size == 2
        assert p._ptrs_size == 0
        x = p._read_primitive(0, Types.int64.ifmt)
        y = p._read_primitive(8, Types.int64.ifmt)
        return x, y
    assert read_point(0) == (10, 100)
    assert read_point(1) == (20, 200)
    assert read_point(2) == (30, 300)
    assert read_point(3) == (40, 400)
    #
    py.test.raises(TypeError, "lst == lst")


def test_text():
    buf = (b'\x01\x00\x00\x00\x82\x00\x00\x00'   # ptrlist
           b'hello capnproto\0')                 # string
    blob = Struct.from_buffer(buf, 0, data_size=0, ptrs_size=1)
    s = blob._read_text_bytes(0)
    assert s == b'hello capnproto'

def test_text_with_offset():
    buf = (b'abcd'                               # some random garbage
           b'\x01\x00\x00\x00\x82\x00\x00\x00'   # ptrlist
           b'hello capnproto\0')                 # string
    blob = Struct.from_buffer(buf, 4, data_size=0, ptrs_size=1)
    s = blob._read_text_bytes(0)
    assert s == b'hello capnproto'

def test_data():
    buf = b('\x01\x00\x00\x00\x42\x00\x00\x00'   # ptrlist
           'A' 'B' 'C' 'D' 'E' 'F' 'G' 'H')     # data
    blob = Struct.from_buffer(buf, 0, data_size=0, ptrs_size=1)
    s = blob._read_data(0)
    assert s == b'ABCDEFGH'


def test_Float64List():
    buf = b('\x01\x00\x00\x00\x25\x00\x00\x00'   # ptrlist
           '\x58\x39\xb4\xc8\x76\xbe\xf3\x3f'   # 1.234
           '\xc3\xf5\x28\x5c\x8f\xc2\x02\x40'   # 2.345
           '\xd9\xce\xf7\x53\xe3\xa5\x0b\x40'   # 3.456
           '\xf8\x53\xe3\xa5\x9b\x44\x12\x40')  # 4.567
    blob = Struct.from_buffer(buf, 0, data_size=0, ptrs_size=1)
    lst = blob._read_list(0, PrimitiveItemType(Types.float64))
    assert list(lst) == [1.234, 2.345, 3.456, 4.567]


def test_Int8List():
    buf = b('\x01\x00\x00\x00\x82\x00\x00\x00'   # ptrlist
           'hello capnproto\0')                 # string
    blob = Struct.from_buffer(buf, 0, data_size=0, ptrs_size=1)
    lst = blob._read_list(0, PrimitiveItemType(Types.int8))
    assert len(lst) == 16
    assert list(lst) == list(map(ord, 'hello capnproto\0'))


def test_list_of_text():
    buf = b('\x01\x00\x00\x00\x26\x00\x00\x00'   # ptrlist
           '\x0d\x00\x00\x00\x12\x00\x00\x00'   # ptr item 1
           '\x0d\x00\x00\x00\x1a\x00\x00\x00'   # ptr item 2
           '\x0d\x00\x00\x00\x22\x00\x00\x00'   # ptr item 3
           '\x0d\x00\x00\x00\x2a\x00\x00\x00'   # ptr item 4
           'A' '\x00\x00\x00\x00\x00\x00\x00'   # A
           'B' 'C' '\x00\x00\x00\x00\x00\x00'   # BC
           'D' 'E' 'F' '\x00\x00\x00\x00\x00'   # DEF
           'G' 'H' 'I' 'J' '\x00\x00\x00\x00')  # GHIJ
    blob = Struct.from_buffer(buf, 0, data_size=0, ptrs_size=1)
    lst = blob._read_list(0, TextItemType(Types.text))
    assert list(lst) == [b'A', b'BC', b'DEF', b'GHIJ']

def test_list_of_text_composite():
    buf = b('\x01\x00\x00\x00\x27\x00\x00\x00'   # ptr<cmp>
           '\x10\x00\x00\x00\x00\x00\x01\x00'   # TAG: 4 items, data=0, ptrs=1
           '\x0d\x00\x00\x00\x12\x00\x00\x00'   # ptr item 1
           '\x0d\x00\x00\x00\x1a\x00\x00\x00'   # ptr item 2
           '\x0d\x00\x00\x00\x22\x00\x00\x00'   # ptr item 3
           '\x0d\x00\x00\x00\x2a\x00\x00\x00'   # ptr item 4
           'A' '\x00\x00\x00\x00\x00\x00\x00'   # A
           'B' 'C' '\x00\x00\x00\x00\x00\x00'   # BC
           'D' 'E' 'F' '\x00\x00\x00\x00\x00'   # DEF
           'G' 'H' 'I' 'J' '\x00\x00\x00\x00')  # GHIJ
    blob = Struct.from_buffer(buf, 0, data_size=0, ptrs_size=1)
    lst = blob._read_list(0, TextItemType(Types.text))
    assert list(lst) == [b'A', b'BC', b'DEF', b'GHIJ']

def test_list_of_text_unicode():
    buf = b('\x01\x00\x00\x00\x26\x00\x00\x00'   # ptrlist
           '\x0d\x00\x00\x00\x12\x00\x00\x00'   # ptr item 1
           '\x0d\x00\x00\x00\x1a\x00\x00\x00'   # ptr item 2
           '\x0d\x00\x00\x00\x22\x00\x00\x00'   # ptr item 3
           '\x0d\x00\x00\x00\x2a\x00\x00\x00'   # ptr item 4
           'A' '\x00\x00\x00\x00\x00\x00\x00'   # A
           '\xc3\xa0\x00\x00\x00\x00\x00\x00'   # à
           'D' 'E' 'F' '\x00\x00\x00\x00\x00'   # DEF
           '\xc3\xa8\xc3\xac\x00\x00\x00\x00')  # èì
    blob = Struct.from_buffer(buf, 0, data_size=0, ptrs_size=1)
    lst = blob._read_list(0, TextUnicodeItemType(Types.text))
    assert list(lst) == [u'A', u'à', u'DEF', u'èì']


def test_list_comparisons():
    buf1 = b('\x01\x00\x00\x00\x00\x00\x00\x00'   # 1
            '\x02\x00\x00\x00\x00\x00\x00\x00'   # 2
            '\x03\x00\x00\x00\x00\x00\x00\x00'   # 3
            '\x04\x00\x00\x00\x00\x00\x00\x00')  # 4
    buf2 = b'garbage0' + buf1
    #
    lst1 = List.from_buffer(buf1, 0, ptr.LIST_SIZE_64, 4, PrimitiveItemType(Types.int64))
    lst2 = List.from_buffer(buf2, 8, ptr.LIST_SIZE_64, 4, PrimitiveItemType(Types.int64))
    lst3 = List.from_buffer(buf1, 0, ptr.LIST_SIZE_64, 3, PrimitiveItemType(Types.int64))
    #
    assert lst1 == lst2
    assert not lst1 != lst2
    #
    assert not lst1 == lst3 # different item_count
    assert lst1 != lst3
    #
    py.test.raises(TypeError, "lst1 <  lst2")
    py.test.raises(TypeError, "lst1 <= lst2")
    py.test.raises(TypeError, "lst1 >  lst2")
    py.test.raises(TypeError, "lst1 >= lst2")

def test_compare_with_py_list():
    buf = b('\x01\x00\x00\x00\x25\x00\x00\x00'   # ptrlist
           '\x01\x00\x00\x00\x00\x00\x00\x00'   # 1
           '\x02\x00\x00\x00\x00\x00\x00\x00'   # 2
           '\x03\x00\x00\x00\x00\x00\x00\x00'   # 3
           '\x04\x00\x00\x00\x00\x00\x00\x00')  # 4
    blob = Struct.from_buffer(buf, 0, data_size=0, ptrs_size=1)
    lst = blob._read_list(0, PrimitiveItemType(Types.int64))
    assert lst == [1, 2, 3, 4]

def test_far_pointer_0():
    # see also test_blob.test_far_pointer_0
    seg0 = b('\x00\x00\x00\x00\x00\x00\x00\x00'   # some garbage
            '\x0a\x00\x00\x00\x01\x00\x00\x00')   # far pointer: segment=1, offset=1
    seg1 = b('\x00\x00\x00\x00\x00\x00\x00\x00'   # random data
            '\x01\x00\x00\x00\x25\x00\x00\x00'    # ptrlist
            '\x01\x00\x00\x00\x00\x00\x00\x00'    # 1
            '\x02\x00\x00\x00\x00\x00\x00\x00'    # 2
            '\x03\x00\x00\x00\x00\x00\x00\x00'    # 3
            '\x04\x00\x00\x00\x00\x00\x00\x00')   # 4
    buf = MultiSegment(seg0+seg1, segment_offsets=(0, 16))
    blob = Struct.from_buffer(buf, 8, data_size=0, ptrs_size=1)
    lst = blob._read_list(0, PrimitiveItemType(Types.int64))
    assert lst == [1, 2, 3, 4]

def test_far_pointer_1():
    # see also test_blob.test_far_pointer_1
    seg0 = b('\x00\x00\x00\x00\x00\x00\x00\x00'   # some garbage
            '\x0e\x00\x00\x00\x02\x00\x00\x00')   # far ptr: pad=1, segment=2, offset=1
                                                  # ==> 2nd line of seg2

    seg1 = b('\x00\x00\x00\x00\x00\x00\x00\x00'   # garbage
            '\x01\x00\x00\x00\x00\x00\x00\x00'    # 1
            '\x02\x00\x00\x00\x00\x00\x00\x00'    # 2
            '\x03\x00\x00\x00\x00\x00\x00\x00'    # 3
            '\x04\x00\x00\x00\x00\x00\x00\x00')   # 4

    seg2 = b('\x00\x00\x00\x00\x00\x00\x00\x00'   # garbage
             '\x0a\x00\x00\x00\x01\x00\x00\x00'   # far ptr: pad=0, segment=1, offset=1
                                                  # ==> 2nd line of seg1
             '\x01\x00\x00\x00\x25\x00\x00\x00')  # tag: ptrlist

    buf = MultiSegment(seg0+seg1+seg2,
                       segment_offsets=(0, len(seg0), len(seg0+seg1)))
    blob = Struct.from_buffer(buf, 8, data_size=0, ptrs_size=1)
    lst = blob._read_list(0, PrimitiveItemType(Types.int64))
    assert lst == [1, 2, 3, 4]



def test_TextItem_far_pointer():
    seg0 = b('\x01\x00\x00\x00\x26\x00\x00\x00'   # ptrlist
             '\x0d\x00\x00\x00\x12\x00\x00\x00'   # ptr item 1
             '\x0d\x00\x00\x00\x1a\x00\x00\x00'   # ptr item 2
             '\x0d\x00\x00\x00\x22\x00\x00\x00'   # ptr item 3
             '\x02\x00\x00\x00\x01\x00\x00\x00'   # far ptr, segment=1, offset=0
             'A' '\x00\x00\x00\x00\x00\x00\x00'   # A
             'B' 'C' '\x00\x00\x00\x00\x00\x00'   # BC
             'D' 'E' 'F' '\x00\x00\x00\x00\x00')  # DEF
    #
    seg1 = b('\x01\x00\x00\x00\x2a\x00\x00\x00'   # ptr item 4
             'G' 'H' 'I' 'J' '\x00\x00\x00\x00')  # GHIJ
    #
    buf = MultiSegment(seg0+seg1, segment_offsets=(0, len(seg0)))
    blob = Struct.from_buffer(buf, 0, data_size=0, ptrs_size=1)
    lst = blob._read_list(0, TextItemType(Types.text))
    assert list(lst) == [b'A', b'BC', b'DEF', b'GHIJ']


def test_ListItem_far_pointer():
    seg0 = b('\x01\x00\x00\x00\x26\x00\x00\x00'   # ptrlist
             '\x0d\x00\x00\x00\x12\x00\x00\x00'   # ptr item 1
             '\x0d\x00\x00\x00\x1a\x00\x00\x00'   # ptr item 2
             '\x0d\x00\x00\x00\x22\x00\x00\x00'   # ptr item 3
             '\x02\x00\x00\x00\x01\x00\x00\x00'   # far ptr, segment=1, offset=0
             'A' '\x00\x00\x00\x00\x00\x00\x00'   # A
             'B' 'C' '\x00\x00\x00\x00\x00\x00'   # BC
             'D' 'E' 'F' '\x00\x00\x00\x00\x00')  # DEF
    #
    seg1 = b('\x01\x00\x00\x00\x2a\x00\x00\x00'   # ptr item 4
             'G' 'H' 'I' 'J' '\x00\x00\x00\x00')  # GHIJ
    #
    buf = MultiSegment(seg0+seg1, segment_offsets=(0, len(seg0)))
    blob = Struct.from_buffer(buf, 0, data_size=0, ptrs_size=1)
    item_type = ListItemType(PrimitiveItemType(Types.int8))
    lst = blob._read_list(0, item_type)
    ghij = lst[3]
    assert list(ghij) == [ord('G'), ord('H'), ord('I'), ord('J'), 0]


def test_ItemType_from_type():
    from capnpy.enum import enum
    def check(t, expected_cls, expected_t=None):
        if expected_t is None:
            expected_t = t
        itemtype = ItemType.from_type(t)
        assert isinstance(itemtype, expected_cls)
        assert itemtype.get_type() is expected_t

    class MyStruct(Struct):
        __static_data_size__ = 0
        __static_ptrs_size__ = 0
    MyEnum = enum('MyEnum', ('a', 'b'))

    check(Types.void, VoidItemType)
    check(Types.bool, BoolItemType)
    check(Types.int8, PrimitiveItemType)
    check(Types.uint8, PrimitiveItemType)
    check(Types.int16, PrimitiveItemType)
    check(Types.uint16, PrimitiveItemType)
    check(Types.int32, PrimitiveItemType)
    check(Types.uint32, PrimitiveItemType)
    check(Types.int64, PrimitiveItemType)
    check(Types.uint64, PrimitiveItemType)
    check(Types.float32, PrimitiveItemType)
    check(Types.float64, PrimitiveItemType)
    check(Types.data, TextItemType)
    check(int, PrimitiveItemType, Types.int64)
    check(float, PrimitiveItemType, Types.float64)
    check(bytes, TextItemType, Types.text)
    check(six.text_type, TextUnicodeItemType, Types.text)
    check(MyStruct, StructItemType)
    check(MyEnum, EnumItemType)
    with pytest.raises(NotImplementedError):
        ItemType.from_type(Types.text)
    #
    # check lists
    itype = ItemType.from_type([int])
    assert isinstance(itype, ListItemType)
    assert itype.inner_item_type.get_type() is Types.int64


class TestPythonicInterface(object):

    @py.test.fixture
    def mylist(self):
        buf = b('\x01\x00\x00\x00\x2D\x00\x00\x00'   # ptrlist
               '\x00\x00\x00\x00\x00\x00\x00\x00'   # 0
               '\x01\x00\x00\x00\x00\x00\x00\x00'   # 1
               '\x02\x00\x00\x00\x00\x00\x00\x00'   # 2
               '\x03\x00\x00\x00\x00\x00\x00\x00'   # 3
               '\x04\x00\x00\x00\x00\x00\x00\x00')  # 4
        blob = Struct.from_buffer(buf, 0, data_size=0, ptrs_size=1)
        lst = blob._read_list(0, PrimitiveItemType(Types.int64))
        return lst

    def test_len(self, mylist):
        assert len(mylist) == 5

    def test_getitem(self, mylist):
        assert mylist[0] == 0
        assert mylist[3] == 3
        assert mylist[-1] == 4
        py.test.raises(IndexError, "mylist[5]")
        py.test.raises(IndexError, "mylist[-6]")

    def test_slice(self, mylist):
        assert mylist[2:4] == [2, 3]
        assert mylist[:3] == [0, 1, 2]
        assert mylist[3:] == [3, 4]
        assert mylist[:] == [0, 1, 2, 3, 4]

