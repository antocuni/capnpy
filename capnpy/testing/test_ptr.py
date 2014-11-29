import struct
from capnpy.ptr import PtrStruct, PtrList

def test_PtrStruct():
    #       0004             ptrs size
    #           0002         data size
    #               00000190 offset<<2
    #                      0 kind
    ptr = 0x0004000200000190
    ptr = PtrStruct(ptr)
    assert ptr.kind == PtrStruct.KIND
    assert ptr.offset == 100
    assert ptr.data_size == 2
    assert ptr.ptrs_size == 4

def test_PtrStruct_new():
    ptr = PtrStruct.new(100*8, 2*8, 4*8)
    assert ptr.kind == PtrStruct.KIND
    assert ptr.offset == 100
    assert ptr.data_size == 2
    assert ptr.ptrs_size == 4
    assert ptr == 0x0004000200000190


def test_PtrList():
    #       0000064          item_count<<1
    #              7         item_size
    #               00000100 offset<<2
    #                      1 kind
    ptr = 0x0000064700000101
    ptr = PtrList(ptr)
    assert ptr.kind == PtrList.KIND
    assert ptr.offset == 64
    assert ptr.size_tag == 7
    assert ptr.item_count == 200
