from capnpy.segment.segment import Segment
from capnpy.anypointer import AnyPointer
from capnpy.struct_ import Struct

def test_as_struct():
    seg = Segment('\x00\x00\x00\x00\x02\x00\x00\x00'   # ptr to 8
                  '\x01\x00\x00\x00\x00\x00\x00\x00'   # 1
                  '\x02\x00\x00\x00\x00\x00\x00\x00')  # 2
    p = seg.read_ptr(0)
    anyp = AnyPointer(seg, 0, p)
    assert anyp.is_struct()
    s = anyp.as_struct(Struct)
    assert isinstance(s, Struct)
    assert s._data_offset == 8
    assert s._ptrs_offset == 24
    assert s._data_size == 2
    assert s._ptrs_size == 0

