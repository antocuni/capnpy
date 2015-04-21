import py
from capnpy import field
from capnpy.struct_ import Struct, Types
from capnpy.list import PrimitiveList, StructList, StringList
from capnpy.enum import enum

def test_primitive():
    class Point(Struct):
        x = field.Primitive('x', 0, Types.int64)
        y = field.Primitive('y', 8, Types.int64)
    
    buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
           '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
    p = Point.from_buffer(buf, 0, None)
    assert p.x == 1
    assert p.y == 2
    assert isinstance(Point.x, field.Primitive)
    assert Point.x.offset == 0
    assert Point.x.type == Types.int64
    assert repr(Point.x) == "<Field x +0: Primitive, type=int64>"


def test_bool():
    class Foo(Struct):
        a = field.Bool('a', 0, 0)
        b = field.Bool('b', 0, 1)
        c = field.Bool('c', 0, 2)

    buf = '\x05\x00\x00\x00\x00\x00\x00\x00'   # True, False, True, padding
    p = Foo.from_buffer(buf, 0, None)
    assert p.a == True
    assert p.b == False
    assert p.c == True


def test_default_value():
    class Foo(Struct):
        x = field.Primitive('x', 0, Types.int64, default=42)
        y = field.Bool('y', 8, 0, default=True)
    
    buf = ('\x00\x00\x00\x00\x00\x00\x00\x00'
           '\x00\x00\x00\x00\x00\x00\x00\x00')
    p = Foo.from_buffer(buf, 0, None)
    assert p.x == 42
    assert p.y is True
    #
    buf = ('\x2a\x00\x00\x00\x00\x00\x00\x00'
           '\x01\x00\x00\x00\x00\x00\x00\x00')
    p = Foo.from_buffer(buf, 0, None)
    assert p.x == 0
    assert p.y is False
    #
    assert repr(Foo.x) == "<Field x +0: Primitive, type=int64, default=42>"
    assert repr(Foo.y) == "<Field y +8: Bool, bitno=0, default=True>"
    


def test_string():
    class Foo(Struct):
        name = field.String('name', 0)

    buf = ('\x01\x00\x00\x00\x82\x00\x00\x00'   # ptrlist
           'hello capnproto\0')                 # string

    f = Foo.from_buffer(buf, 0, None)
    assert f.name == 'hello capnproto'
    assert repr(Foo.name) == '<Field name +0: String>'

def test_data():
    class Foo(Struct):
        data = field.Data('data', 0)

    buf = ('\x01\x00\x00\x00\x42\x00\x00\x00'   # ptrlist
           'A' 'B' 'C' 'D' 'E' 'F' 'G' 'H')     # data

    f = Foo.from_buffer(buf, 0, None)
    assert f.data == 'ABCDEFGH'
    assert repr(Foo.data) == '<Field data +0: Data>'


def test_list():
    class Foo(Struct):
        items = field.List('items', 0, Types.int64)
    
    buf = ('\x01\x00\x00\x00\x25\x00\x00\x00'   # ptrlist
           '\x01\x00\x00\x00\x00\x00\x00\x00'   # 1
           '\x02\x00\x00\x00\x00\x00\x00\x00'   # 2
           '\x03\x00\x00\x00\x00\x00\x00\x00'   # 3
           '\x04\x00\x00\x00\x00\x00\x00\x00')  # 4
    f = Foo.from_buffer(buf, 0, None)
    assert f.items == [1, 2, 3, 4]
    assert repr(Foo.items) == ("<Field items +0: List, listcls=PrimitiveList, "
                               "item_type=<capnp type int64>>")


def test_struct():
    class Point(Struct):
        x = field.Primitive('x', 0, Types.int64)
        y = field.Primitive('y', 8, Types.int64)

    class Rectangle(Struct):
        a = field.Struct('a', 0, Point)
        b = field.Struct('b', 8, Point)

    buf = ('\x04\x00\x00\x00\x02\x00\x00\x00'    # ptr to a
           '\x08\x00\x00\x00\x02\x00\x00\x00'    # ptr to b
           '\x01\x00\x00\x00\x00\x00\x00\x00'    # a.x == 1
           '\x02\x00\x00\x00\x00\x00\x00\x00'    # a.y == 2
           '\x03\x00\x00\x00\x00\x00\x00\x00'    # b.x == 3
           '\x04\x00\x00\x00\x00\x00\x00\x00')   # b.y == 4

    r = Rectangle.from_buffer(buf, 0, None)
    assert r.a.x == 1
    assert r.a.y == 2
    assert r.b.x == 3
    assert r.b.y == 4
    assert repr(Rectangle.a) == "<Field a +0: Struct, structcls=Point>"


def test_enum():
    Color = enum('Color', ('red', 'green', 'blue', 'yellow'))
    Gender = enum('Gender', ('male', 'female', 'unknown'))
    class Foo(Struct):
        color = field.Enum('color', 0, Color)
        gender = field.Enum('gender', 2, Gender)
    
    #      color      gender     padding
    buf = '\x02\x00' '\x01\x00' '\x00\x00\x00\x00'
    f = Foo.from_buffer(buf, 0, None)
    assert f.color == Color.blue
    assert f.gender == Gender.female
    assert repr(Foo.color) == "<Field color +0: Enum, enumcls=Color>"

def test_void():
    class Foo(Struct):
        myvoid = field.Void('myvoid')
    
    f = Foo.from_buffer('somedata', 0, None)
    assert f.myvoid is None
    assert repr(Foo.myvoid) == "<Field myvoid: Void>"

def test_union():
    ## struct Shape {
    ##   area @0 :Int64;
    ##   union {
    ##     circle @1 :Int64;      # radius
    ##     square @2 :Int64;      # width
    ##   }
    ## }
    class Shape(Struct):
        __tag_offset__ = 16
        __tag__ = enum('Shape.__tag__', ('circle', 'square'))

        area = field.Primitive('area', 0, Types.int64)
        circle = field.Union(__tag__.circle, field.Primitive('circle', 8, Types.int64))
        square = field.Union(__tag__.square, field.Primitive('square', 8, Types.int64))

    buf = ('\x40\x00\x00\x00\x00\x00\x00\x00'     # area == 64
           '\x08\x00\x00\x00\x00\x00\x00\x00'     # square == 8
           '\x01\x00\x00\x00\x00\x00\x00\x00')    # which() == square, padding
    shape = Shape.from_buffer(buf, 0, None)
    assert shape.area == 64
    assert shape.which() == Shape.__tag__.square
    assert shape.square == 8
    py.test.raises(ValueError, "shape.circle")
    assert repr(Shape.square) == "<Union square: <Field square +8: Primitive, type=int64>>"


def test_read_group():
    ## struct Rectangle {
    ##     a :group {
    ##         x @0 :Int64;
    ##         y @1 :Int64;
    ##     }
    ##     b :group {
    ##         x @2 :Int64;
    ##         y @3 :Int64;
    ##     }
    ## }
    class Rectangle(Struct):

        @field.Group
        class a(Struct):
            x = field.Primitive('x', 0, Types.int64)
            y = field.Primitive('y', 8, Types.int64)

        @field.Group
        class b(Struct):
            x = field.Primitive('x', 16, Types.int64)
            y = field.Primitive('y', 24, Types.int64)

    buf = ('garbage0'
           '\x01\x00\x00\x00\x00\x00\x00\x00'    # a.x == 1
           '\x02\x00\x00\x00\x00\x00\x00\x00'    # a.y == 2
           '\x03\x00\x00\x00\x00\x00\x00\x00'    # b.x == 3
           '\x04\x00\x00\x00\x00\x00\x00\x00')   # b.y == 4
    #
    # Note that the offsets inside groups are always "absolute" from the
    # beginning of the struct. So, a.x has offset 0, b.x has offset 3.
    #
    r = Rectangle.from_buffer(buf, 8, None)
    assert r.a.x == 1
    assert r.a.y == 2
    assert r.b.x == 3
    assert r.b.y == 4
    assert repr(Rectangle.a) == '<Group a>'


def test_group_union():
    ## struct Shape {
    ##   union {
    ##     circle :group {
    ##       radius @0 :Int64;
    ##     }
    ##     rectangle :group {
    ##       width @1 :Int64;
    ##       height @2 :Int64;
    ##     }
    ##   }
    ## }
    class Shape(Struct):
        __tag_offset__ = 8
        __tag__ = enum('Shape.__tag__', ('circle', 'rectangle'))

        @field.Group
        class circle(Struct):
            radius = field.Primitive('radius', 0, Types.int64)
        circle = field.Union(__tag__.circle, circle)

        @field.Group
        class rectangle(Struct):
            width = field.Primitive('width', 0, Types.int64)
            height = field.Primitive('height', 16, Types.int64)
        rectangle = field.Union(__tag__.rectangle, rectangle)

    buf = ('\x04\x00\x00\x00\x00\x00\x00\x00'    # rectangle.width == 4
           '\x01\x00\x00\x00\x00\x00\x00\x00'    # which() == rectangle, padding
           '\x05\x00\x00\x00\x00\x00\x00\x00')   # rectangle.height == 5

    shape = Shape.from_buffer(buf, 0, None)
    assert shape.which() == Shape.__tag__.rectangle
    assert shape.rectangle.width == 4
    assert shape.rectangle.height == 5
    py.test.raises(ValueError, "shape.circle.radius")

def test_anyPointer():
    class Foo(Struct):
        x = field.AnyPointer('x', 0)

    f = Foo.from_buffer('somedata', 0, None)
    py.test.raises(ValueError, "f.x")
    assert repr(Foo.x) == '<Field x +0: AnyPointer>'


def test_nullable():
    class Foo(Struct):
        x_is_null = field.Primitive('x_is_null', 0, Types.int64)
        x = field.Primitive('x', 8, Types.int64)
        x = field.Nullable(x, x_is_null)

    buf = ('\x00\x00\x00\x00\x00\x00\x00\x00'  # 0
           '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
    p = Foo.from_buffer(buf, 0, None)
    assert p.x_is_null == 0
    assert p.x == 2
    #
    buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 0
           '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
    p = Foo.from_buffer(buf, 0, None)
    assert p.x_is_null == 1
    assert p.x is None
    #
    assert repr(Foo.x) == ('<<Field x +8: Primitive, type=int64>, '
                           'NULL when <Field x_is_null +0: Primitive, type=int64>>')
