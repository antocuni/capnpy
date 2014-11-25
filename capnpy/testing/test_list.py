import py
from capnpy.blob import Blob
from capnpy.list import Int64List, StructList

def test_read_list():
    buf = ('\x01\x00\x00\x00\x25\x00\x00\x00'   # ptrlist
           '\x01\x00\x00\x00\x00\x00\x00\x00'   # 1
           '\x02\x00\x00\x00\x00\x00\x00\x00'   # 2
           '\x03\x00\x00\x00\x00\x00\x00\x00'   # 3
           '\x04\x00\x00\x00\x00\x00\x00\x00')  # 4
    blob = Blob(buf, 0)
    lst = blob._read_list(0, Int64List)
    assert lst._buf is blob._buf
    assert lst._offset == 8
    assert lst._item_count == 4
    assert lst._item_size == 8
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
    blob = Blob(buf, 0)
    lst = blob._read_list(0, Int64List)
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
    blob = Blob(buf, 0)
    lst = blob._read_list(0, StructList, Blob)
    assert lst._buf is blob._buf
    assert lst._offset == 16
    assert lst._item_count == 4
    assert lst._item_size == 16
    #
    assert len(lst) == 4
    def read_point(i):
        p = lst[i]
        return p._read_int64(0), p._read_int64(8)
    assert read_point(0) == (10, 100)
    assert read_point(1) == (20, 200)
    assert read_point(2) == (30, 300)
    assert read_point(3) == (40, 400)
