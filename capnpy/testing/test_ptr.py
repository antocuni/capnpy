import struct
from capnpy.ptr import Ptr, PtrStruct, PtrList

def test_Ptr_generic():
    ptr = Ptr(0x0004000200000190)
    assert ptr.kind == PtrStruct.KIND
    assert ptr.offset == 100
    ptr2 = ptr.specialize()
    assert isinstance(ptr2, PtrStruct)
    #
    ptr = Ptr(0x0000064700000101)
    ptr2 = ptr.specialize()
    assert isinstance(ptr2, PtrList)

def test_Ptr_deref():
    ptr = Ptr(0x0004000200000190)
    assert ptr.offset == 100
    offset = ptr.deref(8)
    assert offset == 816

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
    assert ptr.get_size() == (2, 4)

def test_PtrStruct_new():
    ptr = PtrStruct.new(100, 2, 4)
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

def test_PtrList_new():
    ptr = PtrList.new(64, 7, 200)
    assert ptr.kind == PtrList.KIND
    assert ptr.offset == 64
    assert ptr.size_tag == 7
    assert ptr.item_count == 200
    assert ptr == 0x0000064700000101

