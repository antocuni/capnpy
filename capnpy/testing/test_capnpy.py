from capnpy.struct_ import Struct

def test_Struct():
    # buf is an array of int64 == [1, 2]
    buf = '\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00'
    s1 = Struct.from_buffer(buf, 0)
    assert s1._read_int64(0) == 1
    assert s1._read_int64(8) == 2
    #
    s2 = Struct.from_buffer(buf, 8)
    assert s2._read_int64(0) == 2
