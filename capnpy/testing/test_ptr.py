import struct
from capnpy import ptr

def test_kind_offset():
    p = 0x0004000200000190
    assert ptr.kind(p) == ptr.STRUCT
    assert ptr.offset(p) == 100
    #
    p2 = 0x0000064700000101
    assert ptr.kind(p2) == ptr.LIST


def test_deref():
    p = 0x0004000200000190
    assert ptr.offset(p) == 100
    offset = ptr.deref(p, 8)
    assert offset == 816

def test_struct_ptr():
    #       0004             ptrs size
    #           0002         data size
    #               00000190 offset<<2
    #                      0 kind
    p = 0x0004000200000190
    assert ptr.kind(p) == ptr.STRUCT
    assert ptr.offset(p) == 100
    assert ptr.struct_data_size(p) == 2
    assert ptr.struct_ptrs_size(p) == 4

def test_new_struct():
    p = ptr.new_struct(100, 2, 4)
    assert ptr.kind(p) == ptr.STRUCT
    assert ptr.offset(p) == 100
    assert ptr.struct_data_size(p) == 2
    assert ptr.struct_ptrs_size(p) == 4
    assert p == 0x0004000200000190

def test_ListPtr():
    #       0000064          item_count<<1
    #              7         item_size
    #               00000100 offset<<2
    #                      1 kind
    p = 0x0000064700000101
    assert ptr.kind(p) == ptr.LIST
    assert ptr.offset(p) == 64
    assert ptr.list_size_tag(p) == 7
    assert ptr.list_item_count(p) == 200

def test_new_list():
    p = ptr.new_list(64, 7, 200)
    assert ptr.kind(p) == ptr.LIST
    assert ptr.offset(p) == 64
    assert ptr.list_size_tag(p) == 7
    assert ptr.list_item_count(p) == 200
    assert p == 0x0000064700000101

def test_list_item_length():
    assert ptr.list_item_length(ptr.LIST_SIZE_VOID) == 0
    assert ptr.list_item_length(ptr.LIST_SIZE_BIT) == -1
    assert ptr.list_item_length(ptr.LIST_SIZE_8) == 1
    assert ptr.list_item_length(ptr.LIST_SIZE_16) == 2
    assert ptr.list_item_length(ptr.LIST_SIZE_32) == 4
    assert ptr.list_item_length(ptr.LIST_SIZE_64) == 8
    assert ptr.list_item_length(ptr.LIST_SIZE_PTR) == 8
    assert ptr.list_item_length(ptr.LIST_SIZE_COMPOSITE) == -1

def test_signedness():
    #       0000001          item_count<<1
    #              7         item_size
    #               ffffffe0 offset<<2
    #                      1 kind
    p = 0x00000017ffffffe1
    assert ptr.offset(p) == -8

def test_FarPtr():
    #       00000001         target
    #               000016aa offset
    #                      a landing
    #                      a kind
    p = 0x00000001000016aa
    assert ptr.kind(p) == ptr.FAR
    assert ptr.far_landing_pad(p) == 0
    assert ptr.far_offset(p) == 725
    assert ptr.far_target(p) == 1

def test_new_far():
    p = ptr.new_far(0, 725, 1)
    assert ptr.kind(p) == ptr.FAR
    assert ptr.far_landing_pad(p) == 0
    assert ptr.far_offset(p) == 725
    assert ptr.far_target(p) == 1
    assert p == 0x00000001000016aa

def test_new_struct_overflow():
    def unpack(p):
        assert ptr.kind(p) == ptr.STRUCT
        return ptr.offset(p), ptr.struct_data_size(p), ptr.struct_ptrs_size(p)
    #
    p = ptr.new_struct(-1, 0, 0)
    assert unpack(p) == (-1, 0, 0)
    #
    p = ptr.new_struct(0, -1, 0)
    assert unpack(p) == (0, 2**16-1, 0)
    #
    p = ptr.new_struct(0, 0, -1)
    assert unpack(p) == (0, 0, 2**16-1)

def test_new_list_overflow():
    def unpack(p):
        assert ptr.kind(p) == ptr.LIST
        return ptr.offset(p), ptr.list_size_tag(p), ptr.list_item_count(p)
    #
    p = ptr.new_list(-1, 0, 0)
    assert unpack(p) == (-1, 0, 0)
    #
    p = ptr.new_list(0, -1, 0)
    assert unpack(p) == (0, 7, 0)
    #
    p = ptr.new_list(0, 0, -1)
    assert unpack(p) == (0, 0, 2**29-1)

def test_new_far_overflow():
    def unpack(p):
        assert ptr.kind(p) == ptr.FAR
        return ptr.far_landing_pad(p), ptr.far_offset(p), ptr.far_target(p)
    #
    p = ptr.new_far(-1, 0, 0)
    assert unpack(p) == (1, 0, 0)
    #
    p = ptr.new_far(0, -1, 0)
    assert unpack(p) == (0, 2**29-1, 0)
    #
    p = ptr.new_far(0, 0, -1)
    assert unpack(p) == (0, 0, 2**32-1)

def test_round_up_to_word():
    assert ptr.round_up_to_word(0) == 0
    assert ptr.round_up_to_word(5) == 8
    assert ptr.round_up_to_word(7) == 8
    assert ptr.round_up_to_word(8) == 8
    assert ptr.round_up_to_word(9) == 16
