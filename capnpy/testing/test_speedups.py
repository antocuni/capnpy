import py
from capnpy.type import Types
from capnpy.speedups import BaseBlob, PrimitiveField

def test_BaseBlob():
    blob = BaseBlob.from_buffer('mybuffer', 42, [0, 1, 2])
    assert blob._buf == 'mybuffer'
    assert blob._offset == 42
    assert blob._segment_offsets == [0, 1, 2]

def test_BaseBlob_ctor():
    py.test.raises(NotImplementedError, "BaseBlob()")


def test_PrimitiveField():
    class Point(BaseBlob):
        x = PrimitiveField('x', 0, Types.int64)
        y = PrimitiveField('y', 8, Types.int64)
    
    buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
           '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
    p = Point.from_buffer(buf, 0, None)
    assert p.x == 1
    assert p.y == 2
    assert isinstance(Point.x, PrimitiveField)
    assert Point.x.offset == 0
    assert Point.x.type == Types.int64
