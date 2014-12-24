from capnpy import field
from capnpy.struct_ import Struct, Types
from capnpy.list import PrimitiveList, StructList, StringList

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
    assert repr(Point.x) == "<Field +0: Primitive, type='q'>"
   
def test_string():
    class Foo(Struct):
        name = field.String(0)

    buf = ('\x01\x00\x00\x00\x82\x00\x00\x00'   # ptrlist
           'hello capnproto\0')                 # string

    f = Foo.from_buffer(buf)
    assert f.name == 'hello capnproto'
    assert repr(Foo.name) == '<Field +0: String>'


def test_list():
    class Foo(Struct):
        items = field.List(0, PrimitiveList, Types.Int64)
    
    buf = ('\x01\x00\x00\x00\x25\x00\x00\x00'   # ptrlist
           '\x01\x00\x00\x00\x00\x00\x00\x00'   # 1
           '\x02\x00\x00\x00\x00\x00\x00\x00'   # 2
           '\x03\x00\x00\x00\x00\x00\x00\x00'   # 3
           '\x04\x00\x00\x00\x00\x00\x00\x00')  # 4
    f = Foo.from_buffer(buf, 0)
    assert f.items == [1, 2, 3, 4]
    assert repr(Foo.items) == "<Field +0: List, listcls=PrimitiveList, item_type='q'>"

def test_struct():
    class Point(Struct):
        x = field.Primitive(0, Types.Int64)
        y = field.Primitive(8, Types.Int64)

    class Rectangle(Struct):
        a = field.Struct(0, Point)
        b = field.Struct(8, Point)

    buf = ('\x04\x00\x00\x00\x02\x00\x00\x00'    # ptr to a
           '\x08\x00\x00\x00\x02\x00\x00\x00'    # ptr to b
           '\x01\x00\x00\x00\x00\x00\x00\x00'    # a.x == 1
           '\x02\x00\x00\x00\x00\x00\x00\x00'    # a.y == 2
           '\x03\x00\x00\x00\x00\x00\x00\x00'    # b.x == 3
           '\x04\x00\x00\x00\x00\x00\x00\x00')   # b.y == 4

    r = Rectangle.from_buffer(buf)
    assert r.a.x == 1
    assert r.a.y == 2
    assert r.b.x == 3
    assert r.b.y == 4
    assert repr(Rectangle.a) == "<Field +0: Struct, structcls=Point>"
