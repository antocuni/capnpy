from capnpy import field
from capnpy.struct_ import Struct, Types

def test_primitive():
    class Point(Struct):
        x = field.Primitive(0, Types.Int64)
        y = field.Primitive(8, Types.Int64)
    
    buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
           '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
    p = Point.from_buffer(buf)
    assert p.x == 1
    assert p.y == 2
    assert isinstance(Point.x, field.Primitive)
    assert Point.x.offset == 0
    assert Point.x.type == Types.Int64
    assert repr(Point.x) == "<Field: Primitive, offset=0, type='q'>"
   
def test_string():
    class Foo(Struct):
        name = field.String(0)

    buf = ('\x01\x00\x00\x00\x82\x00\x00\x00'   # ptrlist
           'hello capnproto\0')                 # string

    f = Foo.from_buffer(buf)
    assert f.name == 'hello capnproto'
