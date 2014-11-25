from capnpy.blob import Blob

def test_Blob():
    # buf is an array of int64 == [1, 2]
    buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
           '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
    b1 = Blob(buf, 0)
    assert b1._read_int64(0) == 1
    assert b1._read_int64(8) == 2
    #
    b2 = Blob(buf, 8)
    assert b2._read_int64(0) == 2


def test_ptrstruct():
    buf = '\x90\x01\x00\x00\x02\x00\x04\x00'
    blob = Blob(buf, 0)
    offset, data_size, ptrs_size = blob._unpack_ptrstruct(0)
    assert offset == 100
    assert data_size == 2
    assert ptrs_size == 4
    #
    offset = blob._deref_ptrstruct(0)
    assert offset == 808


def test_ptrlist():
    buf = '\x01\x01\x00\x00G\x06\x00\x00'
    blob = Blob(buf, 0)
    offset, item_size, item_count = blob._unpack_ptrlist(0)
    assert offset == 64
    assert item_size == 7
    assert item_count == 200


def test_read_struct():
    ## struct Point {
    ##   x @0 :Int64;
    ##   y @1 :Int64;
    ## }
    buf = ('\x00\x00\x00\x00\x02\x00\x00\x00'    # ptr to {x, y}
           '\x01\x00\x00\x00\x00\x00\x00\x00'    # x == 1
           '\x02\x00\x00\x00\x00\x00\x00\x00')   # y == 2
    blob = Blob(buf, 0)
    p = blob._read_struct(0, Blob)
    assert p._buf is blob._buf
    assert p._offset == 8
    assert p._read_int64(0) == 1
    assert p._read_int64(8) == 2
