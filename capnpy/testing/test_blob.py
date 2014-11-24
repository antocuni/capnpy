from capnpy.struct_ import Blob

def test_Blob():
    # buf is an array of int64 == [1, 2]
    buf = '\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00'
    b1 = Blob(buf, 0)
    assert b1._read_int64(0) == 1
    assert b1._read_int64(8) == 2
    #
    b2 = Blob(buf, 8)
    assert b2._read_int64(0) == 2


def test_unpack_ptrstruct():
    buf = '\x90\x01\x00\x00\x02\x00\x04\x00'
    blob = Blob(buf, 0)
    offset, data_size, ptrs_size = blob._unpack_ptrstruct(0)
    assert offset == 100
    assert data_size == 2
    assert ptrs_size == 4
