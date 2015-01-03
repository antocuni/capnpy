import py
from capnpy.blob import Blob, Types
from capnpy.ptr import ListPtr
from capnpy.list import PrimitiveList, StructList, StringList

def test_read_list():
    buf = ('\x01\x00\x00\x00\x25\x00\x00\x00'   # ptrlist
           '\x01\x00\x00\x00\x00\x00\x00\x00'   # 1
           '\x02\x00\x00\x00\x00\x00\x00\x00'   # 2
           '\x03\x00\x00\x00\x00\x00\x00\x00'   # 3
           '\x04\x00\x00\x00\x00\x00\x00\x00')  # 4
    blob = Blob.from_buffer(buf, 0)
    lst = blob._read_list(0, PrimitiveList, Types.int64)
    assert lst._buf is blob._buf
    assert lst._offset == 8
    assert lst._item_offset == 0
    assert lst._item_count == 4
    assert lst._item_length == 8
    assert lst._read_list_item(0) == 1
    assert lst._read_list_item(8) == 2
    assert lst._read_list_item(16) == 3
    assert lst._read_list_item(24) == 4

def test_read_list_offset():
    buf = ('abcd'                               # random garbage
           '\x01\x00\x00\x00\x25\x00\x00\x00'   # ptrlist
           '\x01\x00\x00\x00\x00\x00\x00\x00'   # 1
           '\x02\x00\x00\x00\x00\x00\x00\x00'   # 2
           '\x03\x00\x00\x00\x00\x00\x00\x00'   # 3
           '\x04\x00\x00\x00\x00\x00\x00\x00')  # 4
    blob = Blob.from_buffer(buf, 4)
    lst = blob._read_list(0, PrimitiveList, Types.int64)
    assert lst._buf is blob._buf
    assert lst._offset == 12
    assert lst._item_count == 4
    assert lst._item_length == 8
    assert lst._read_list_item(0) == 1
    assert lst._read_list_item(8) == 2
    assert lst._read_list_item(16) == 3
    assert lst._read_list_item(24) == 4

def test_pythonic():
    buf = ('\x01\x00\x00\x00\x25\x00\x00\x00'   # ptrlist
           '\x01\x00\x00\x00\x00\x00\x00\x00'   # 1
           '\x02\x00\x00\x00\x00\x00\x00\x00'   # 2
           '\x03\x00\x00\x00\x00\x00\x00\x00'   # 3
           '\x04\x00\x00\x00\x00\x00\x00\x00')  # 4
    blob = Blob.from_buffer(buf, 0)
    lst = blob._read_list(0, PrimitiveList, Types.int64)
    assert len(lst) == 4
    assert lst[0] == 1
    assert lst[3] == 4
    assert lst[-1] == 4
    py.test.raises(IndexError, "lst[4]")
    py.test.raises(IndexError, "lst[-5]")

def test_list_of_structs():
    # list of Point {x: Int64, y: Int64}
    buf = ('\x01\x00\x00\x00\x47\x00\x00\x00'    # ptrlist
           '\x10\x00\x00\x00\x02\x00\x00\x00'    # list tag
           '\x0a\x00\x00\x00\x00\x00\x00\x00'    # 10
           '\x64\x00\x00\x00\x00\x00\x00\x00'    # 100
           '\x14\x00\x00\x00\x00\x00\x00\x00'    # 20
           '\xc8\x00\x00\x00\x00\x00\x00\x00'    # 200
           '\x1e\x00\x00\x00\x00\x00\x00\x00'    # 30
           '\x2c\x01\x00\x00\x00\x00\x00\x00'    # 300
           '\x28\x00\x00\x00\x00\x00\x00\x00'    # 40
           '\x90\x01\x00\x00\x00\x00\x00\x00')   # 400
    blob = Blob.from_buffer(buf, 0)
    lst = blob._read_list(0, StructList, Blob)
    assert lst._buf is blob._buf
    assert lst._offset == 8
    assert lst._item_offset == 8
    assert lst._item_count == 4
    assert lst._item_length == 16
    #
    assert len(lst) == 4
    def read_point(i):
        p = lst[i]
        x = p._read_primitive(0, Types.int64)
        y = p._read_primitive(8, Types.int64)
        return x, y
    assert read_point(0) == (10, 100)
    assert read_point(1) == (20, 200)
    assert read_point(2) == (30, 300)
    assert read_point(3) == (40, 400)


def test_string():
    buf = ('\x01\x00\x00\x00\x82\x00\x00\x00'   # ptrlist
           'hello capnproto\0')                 # string
    blob = Blob.from_buffer(buf, 0)
    s = blob._read_string(0)
    assert s == 'hello capnproto'

def test_string_with_offset():
    buf = ('abcd'                               # some random garbage
           '\x01\x00\x00\x00\x82\x00\x00\x00'   # ptrlist
           'hello capnproto\0')                 # string
    blob = Blob.from_buffer(buf, 4)
    s = blob._read_string(0)
    assert s == 'hello capnproto'

def test_data():
    buf = ('\x01\x00\x00\x00\x42\x00\x00\x00'   # ptrlist
           'A' 'B' 'C' 'D' 'E' 'F' 'G' 'H')     # data
    blob = Blob.from_buffer(buf, 0)
    s = blob._read_data(0)
    assert s == 'ABCDEFGH'
    

def test_Float64List():
    buf = ('\x01\x00\x00\x00\x25\x00\x00\x00'   # ptrlist
           '\x58\x39\xb4\xc8\x76\xbe\xf3\x3f'   # 1.234
           '\xc3\xf5\x28\x5c\x8f\xc2\x02\x40'   # 2.345
           '\xd9\xce\xf7\x53\xe3\xa5\x0b\x40'   # 3.456
           '\xf8\x53\xe3\xa5\x9b\x44\x12\x40')  # 4.567
    blob = Blob.from_buffer(buf, 0)
    lst = blob._read_list(0, PrimitiveList, Types.float64)
    assert list(lst) == [1.234, 2.345, 3.456, 4.567]


def test_Int8List():
    buf = ('\x01\x00\x00\x00\x82\x00\x00\x00'   # ptrlist
           'hello capnproto\0')                 # string
    blob = Blob.from_buffer(buf, 0)
    lst = blob._read_list(0, PrimitiveList, Types.int8)
    assert len(lst) == 16
    assert list(lst) == map(ord, 'hello capnproto\0')


def test_list_of_strings():
    buf = ('\x01\x00\x00\x00\x26\x00\x00\x00'   # ptrlist
           '\x0d\x00\x00\x00\x12\x00\x00\x00'   # ptr item 1
           '\x0d\x00\x00\x00\x1a\x00\x00\x00'   # ptr item 2
           '\x0d\x00\x00\x00\x22\x00\x00\x00'   # ptr item 3
           '\x0d\x00\x00\x00\x2a\x00\x00\x00'   # ptr item 4
           'A' '\x00\x00\x00\x00\x00\x00\x00'   # A
           'B' 'C' '\x00\x00\x00\x00\x00\x00'   # BC
           'D' 'E' 'F' '\x00\x00\x00\x00\x00'   # DEF
           'G' 'H' 'I' 'J' '\x00\x00\x00\x00')  # GHIJ
    blob = Blob.from_buffer(buf, 0)
    lst = blob._read_list(0, StringList, None)
    assert list(lst) == ['A', 'BC', 'DEF', 'GHIJ']


def test_list_primitive_body_range():
    buf = ('\x01\x00\x00\x00\x82\x00\x00\x00'   # ptrlist
           'hello capnproto\0')                 # string
    blob = Blob.from_buffer(buf, 0)
    lst = blob._read_list(0, PrimitiveList, Types.int8)
    body_start, body_end = lst._get_body_range()
    assert body_start == 8
    assert body_end == 24


def test_list_composite_body_range():
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
           'P' 'o' 'i' 'n' 't' ' ' 'C' '\x00')

    blob = Blob.from_buffer(buf, 8)
    points = blob._read_list(0, StructList, Blob)
    start, end = points._get_body_range()
    assert start == 16
    assert end == 120


def test_list_of_pointers():
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
    
    blob = Blob.from_buffer(buf, 8)
    points = blob._read_list(0, StringList, None)
    start, end = points._get_body_range()
    assert start == 16
    # note that the end if 88, not 86: the last two \x00\x00 are not counted,
    # because they are padding, not actual data
    assert end == 86


def test_list_comparisons():
    buf1 = ('\x01\x00\x00\x00\x00\x00\x00\x00'   # 1
            '\x02\x00\x00\x00\x00\x00\x00\x00'   # 2
            '\x03\x00\x00\x00\x00\x00\x00\x00'   # 3
            '\x04\x00\x00\x00\x00\x00\x00\x00')  # 4
    buf2 = 'garbage0' + buf1
    #
    lst1 = PrimitiveList.from_buffer(buf1, 0, ListPtr.SIZE_64, 4, Types.int64)
    lst2 = PrimitiveList.from_buffer(buf2, 8, ListPtr.SIZE_64, 4, Types.int64)
    lst3 = PrimitiveList.from_buffer(buf1, 0, ListPtr.SIZE_64, 3, Types.int64)
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
    buf = ('\x01\x00\x00\x00\x25\x00\x00\x00'   # ptrlist
           '\x01\x00\x00\x00\x00\x00\x00\x00'   # 1
           '\x02\x00\x00\x00\x00\x00\x00\x00'   # 2
           '\x03\x00\x00\x00\x00\x00\x00\x00'   # 3
           '\x04\x00\x00\x00\x00\x00\x00\x00')  # 4
    blob = Blob.from_buffer(buf, 0)
    lst = blob._read_list(0, PrimitiveList, Types.int64)
    assert lst == [1, 2, 3, 4]
