import struct
from capnpy.ptr import PtrStruct, PtrList

def test_PtrStruct_unpack():
    buf = '\x90\x01\x00\x00\x02\x00\x04\x00'
    ptr = struct.unpack('<q', buf)[0]
    offset, data_size, ptrs_size = PtrStruct.unpack(ptr)
    assert offset == 100
    assert data_size == 2
    assert ptrs_size == 4


def test_ptrlist():
    buf = '\x01\x01\x00\x00G\x06\x00\x00'
    ptr = struct.unpack('<q', buf)[0]
    offset, item_size, item_count = PtrList.unpack(ptr)
    assert offset == 64
    assert item_size == 7
    assert item_count == 200
