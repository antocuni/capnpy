from capnpy.blob import Blob
from capnpy.list import Int64List

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
    assert lst._item_size == lst.LIST_64
    assert lst._read_list_item(0) == 1
    assert lst._read_list_item(8) == 2
    assert lst._read_list_item(16) == 3
    assert lst._read_list_item(24) == 4
