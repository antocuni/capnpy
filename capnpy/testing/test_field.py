import py
from capnpy import field
from capnpy.struct_ import Struct, Types
from capnpy.list import PrimitiveList, StructList, StringList
from capnpy.enum import enum

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


def test_enum():
    Color = enum('Color', ('red', 'green', 'blue', 'yellow'))
    Gender = enum('Gender', ('male', 'female', 'unknown'))
    class Foo(Struct):
        color = field.Enum(0, Color)
        gender = field.Enum(2, Gender)
    
    #      color      gender     padding
    buf = '\x02\x00' '\x01\x00' '\x00\x00\x00\x00'
    f = Foo.from_buffer(buf)
    assert f.color == Color.blue
    assert f.gender == Gender.female
    assert repr(Foo.color) == "<Field +0: Enum, enumcls=Color>"


def test_union():
    ## struct Shape {
    ##   area @0 :Int64;
    ##   union {
    ##     circle @1 :Int64;      # radius
    ##     square @2 :Int64;      # width
    ##   }
    ## }
    class Shape(Struct):
        __union_tag_offset__ = 16
        __union_tag__ = enum('Shape.__union_tag__', ('circle', 'square'))

        area = field.Primitive(0, Types.Int64)
        circle = field.Union(__union_tag__.circle, field.Primitive(8, Types.Int64))
        square = field.Union(__union_tag__.square, field.Primitive(8, Types.Int64))

    buf = ('\x40\x00\x00\x00\x00\x00\x00\x00'     # area == 64
           '\x08\x00\x00\x00\x00\x00\x00\x00'     # square == 8
           '\x01\x00\x00\x00\x00\x00\x00\x00')    # which() == square, padding
    shape = Shape.from_buffer(buf, 0)
    assert shape.area == 64
    assert shape.which() == Shape.__union_tag__.square
    assert shape.square == 8
    py.test.raises(ValueError, "shape.circle")
    assert repr(Shape.square) == "<Union square: <Field +8: Primitive, type='q'>>"
