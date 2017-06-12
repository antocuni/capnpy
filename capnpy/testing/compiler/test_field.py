import py
from capnpy.testing.compiler.support import CompilerTest

class TestField(CompilerTest):

    def test_primitive_plain(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
        }
        """
        mod = self.compile(schema)
        self.check_pyx(mod)
        if self.pyx:
            # the repr starts with 'class' for Python classes but 'type' for
            # classes defined in C. Let's check that mod.Point is actually a
            # cdef class
            assert repr(mod.Point) == "<type 'tmp.Point'>"
        #
        buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
               '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
        p = mod.Point.from_buffer(buf, 0, 2, 0)
        assert p.x == 1
        assert p.y == 2

    def test_primitive_default(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            x @0 :Int64 = 42;
            y @1 :Bool = true;
        }
        """
        mod = self.compile(schema)
        #
        buf = ('\x00\x00\x00\x00\x00\x00\x00\x00'
               '\x00\x00\x00\x00\x00\x00\x00\x00')
        p = mod.Foo.from_buffer(buf, 0, 2, 0)
        assert p.x == 42
        assert p.y is True
        #
        buf = ('\x2a\x00\x00\x00\x00\x00\x00\x00'
               '\x01\x00\x00\x00\x00\x00\x00\x00')
        p = mod.Foo.from_buffer(buf, 0, 2, 0)
        assert p.x == 0
        assert p.y is False


    def test_void(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            x @0 :Void;
        }
        """
        mod = self.compile(schema)
        #
        p = mod.Foo.from_buffer('', 0, 0, 0)
        assert p.x is None


    def test_string(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            x @0 :Int64;
            name @1 :Text;
        }
        """
        mod = self.compile(schema)

        buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'   # 1
               '\x01\x00\x00\x00\x82\x00\x00\x00'   # ptrlist
               'hello capnproto\0')                 # string

        f = mod.Foo.from_buffer(buf, 0, 1, 1)
        assert f.x == 1
        assert f.name == 'hello capnproto'

    def test_data(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            x @0 :Int64;
            data @1 :Data;
        }
        """
        mod = self.compile(schema)
        buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'   # 1
               '\x01\x00\x00\x00\x42\x00\x00\x00'   # ptrlist
               'A' 'B' 'C' 'D' 'E' 'F' 'G' 'H')     # data

        f = mod.Foo.from_buffer(buf, 0, 1, 1)
        assert f.data == 'ABCDEFGH'


    def test_struct(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
        }
        struct Rectangle {
            a @0 :Point;
            b @1 :Point;
        }
        """
        mod = self.compile(schema)
        buf = ('\x04\x00\x00\x00\x02\x00\x00\x00'    # ptr to a
               '\x08\x00\x00\x00\x02\x00\x00\x00'    # ptr to b
               '\x01\x00\x00\x00\x00\x00\x00\x00'    # a.x == 1
               '\x02\x00\x00\x00\x00\x00\x00\x00'    # a.y == 2
               '\x03\x00\x00\x00\x00\x00\x00\x00'    # b.x == 3
               '\x04\x00\x00\x00\x00\x00\x00\x00')   # b.y == 4
        r = mod.Rectangle.from_buffer(buf, 0, 0, 2)
        assert r.a.x == 1
        assert r.a.y == 2
        assert r.b.x == 3
        assert r.b.y == 4

    def test_nested_struct(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Rectangle {
            struct Point {
                x @0 :Int64;
                y @1 :Int64;
            }
            a @0 :Point;
            b @1 :Point;
        }
        """
        mod = self.compile(schema)
        buf = ('\x04\x00\x00\x00\x02\x00\x00\x00'    # ptr to a
               '\x08\x00\x00\x00\x02\x00\x00\x00'    # ptr to b
               '\x01\x00\x00\x00\x00\x00\x00\x00'    # a.x == 1
               '\x02\x00\x00\x00\x00\x00\x00\x00'    # a.y == 2
               '\x03\x00\x00\x00\x00\x00\x00\x00'    # b.x == 3
               '\x04\x00\x00\x00\x00\x00\x00\x00')   # b.y == 4
        r = mod.Rectangle.from_buffer(buf, 0, 0, 2)
        assert r.a.x == 1
        assert r.a.y == 2
        assert r.b.x == 3
        assert r.b.y == 4

    def test_enum_simple(self):
        schema = """
        @0xbf5147cbbecf40c1;
        enum Color {
            red @0;
            green @1;
            blue @2;
            yellow @3;
        }
        enum Gender {
            male @0;
            female @1;
            unknown @2;
        }
        struct Foo {
            color @0 :Color;
            gender @1 :Gender;
        }
        """
        mod = self.compile(schema)
        assert mod.Color.__members__ == ('red', 'green', 'blue', 'yellow')
        #      color      gender     padding
        buf = '\x02\x00' '\x01\x00' '\x00\x00\x00\x00'
        f = mod.Foo.from_buffer(buf, 0, 1, 0)
        assert f.color == mod.Color.blue
        assert f.gender == mod.Gender.female
        #
        # check that we can read values even if they are not statically known
        # at compile time
        buf = '\x04\x00' '\x03\x00' '\x00\x00\x00\x00'
        f = mod.Foo.from_buffer(buf, 0, 1, 0)
        assert f.color == 4
        assert f.gender == 3

    def test_enum_single_member(self):
        schema = """
        @0xbf5147cbbecf40c1;
        enum Color {
            red @0;
        }
        """
        mod = self.compile(schema)
        assert mod.Color.red == 0

    def test_enum_default(self):
        schema = """
        @0xbf5147cbbecf40c1;
        enum Color {
            red @0;
            green @1;
            blue @2;
            yellow @3;
        }
        enum Gender {
            male @0;
            female @1;
            unknown @2;
        }
        struct Foo {
            color @0 :Color = green;
            gender @1 :Gender = female;
        }
        """
        mod = self.compile(schema)
        buf = ''
        f = mod.Foo.from_buffer(buf, 0, 0, 0)
        assert f.color == mod.Color.green
        assert f.gender == mod.Gender.female
        assert str(f.color) == 'green' # that check it's an actual enum and
                                       # not a plain int

    def test_union(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Shape {
          area @0 :Int64;
          union {
            circle @1 :Int64;      # radius
            square @2 :Int64;      # width
            empty  @3 :Void;
          }
        }
        """
        mod = self.compile(schema)
        buf = ('\x40\x00\x00\x00\x00\x00\x00\x00'     # area == 64
               '\x08\x00\x00\x00\x00\x00\x00\x00'     # square == 8
               '\x01\x00\x00\x00\x00\x00\x00\x00')    # which() == square, padding
        shape = mod.Shape.from_buffer(buf, 0, 3, 0)
        assert shape.area == 64
        assert shape.which() == mod.Shape.__tag__.square
        assert shape.square == 8
        py.test.raises(ValueError, "shape.circle")
        py.test.raises(ValueError, "shape.empty")
        #
        buf = ('\x40\x00\x00\x00\x00\x00\x00\x00'     # area == 64
               '\x00\x00\x00\x00\x00\x00\x00\x00'     # unused
               '\x02\x00\x00\x00\x00\x00\x00\x00')    # which() == empty, padding
        shape = mod.Shape.from_buffer(buf, 0, 3, 0)
        assert shape.area == 64
        assert shape.which() == mod.Shape.__tag__.empty
        assert shape.empty is None
        py.test.raises(ValueError, "shape.square")
        py.test.raises(ValueError, "shape.circle")

    def test_which(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Shape {
          area @0 :Int64;
          union {
            circle @1 :Int64;      # radius
            square @2 :Int64;      # width
            empty  @3 :Void;
          }
        }
        struct Foo {
            foo @0 :Int64;
        }
        """
        mod = self.compile(schema)
        shape = mod.Shape.from_buffer('', 0, data_size=0, ptrs_size=0)
        assert shape.which() == mod.Shape.__tag__.circle
        assert type(shape.which()) is mod.Shape.__tag__
        assert shape.__which__() == mod.Shape.__tag__.circle
        assert type(shape.__which__()) is int
        #
        foo = mod.Foo.from_buffer('', 0, data_size=0, ptrs_size=0)
        exc = py.test.raises(TypeError, "foo.which()")
        assert str(exc.value) == 'Cannot call which() on a non-union type'

    def test_is_union(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Shape {
          area @0 :Int64;
          union {
            circle @1 :Int64;      # radius
            square @2 :Int64;      # width
            empty  @3 :Void;
          }
        }
        """
        mod = self.compile(schema)
        buf = ('\x40\x00\x00\x00\x00\x00\x00\x00'     # area == 64
               '\x08\x00\x00\x00\x00\x00\x00\x00'     # square == 8
               '\x01\x00\x00\x00\x00\x00\x00\x00')    # which() == square, padding
        shape = mod.Shape.from_buffer(buf, 0, 3, 0)
        assert shape.is_square()
        assert not shape.is_circle()
        assert not shape.is_empty()


    def test_group(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Rectangle {
            a :group {
                x @0 :Int64;
                y @1 :Int64;
            }
            b :group {
                x @2 :Int64;
                y @3 :Int64;
            }
        }
        """
        mod = self.compile(schema)
        buf = ('garbage0'
               '\x01\x00\x00\x00\x00\x00\x00\x00'    # a.x == 1
               '\x02\x00\x00\x00\x00\x00\x00\x00'    # a.y == 2
               '\x03\x00\x00\x00\x00\x00\x00\x00'    # b.x == 3
               '\x04\x00\x00\x00\x00\x00\x00\x00')   # b.y == 4
        r = mod.Rectangle.from_buffer(buf, 8, 4, 0)
        assert r.a.x == 1
        assert r.a.y == 2
        assert r.b.x == 3
        assert r.b.y == 4

    def test_union_group(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Shape {
          union {
            circle :group {
              radius @0 :Int64;
            }
            rectangle :group {
              width @1 :Int64;
              height @2 :Int64;
            }
          }
        }
        """
        mod = self.compile(schema)
        buf = ('\x04\x00\x00\x00\x00\x00\x00\x00'    # rectangle.width == 4
               '\x01\x00\x00\x00\x00\x00\x00\x00'    # which() == rectangle, padding
               '\x05\x00\x00\x00\x00\x00\x00\x00')   # rectangle.height == 5

        shape = mod.Shape.from_buffer(buf, 0, 3, 0)
        assert shape.which() == mod.Shape.__tag__.rectangle
        assert shape.rectangle.width == 4
        assert shape.rectangle.height == 5
        py.test.raises(ValueError, "shape.circle.radius")

    def test_bool(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            padding @0 :Int64;
            a @1 :Bool;
            b @2 :Bool;
            c @3 :Bool;
        }
        """
        mod = self.compile(schema)
        buf = ('\x00\x00\x00\x00\x00\x00\x00\x00'   # padding
               '\x05\x00\x00\x00\x00\x00\x00\x00')  # True, False, True, padding
        p = mod.Foo.from_buffer(buf, 0, 2, 0)
        assert p.a == True
        assert p.b == False
        assert p.c == True

    def test_anyPointer(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            x @0 :AnyPointer;
        }
        """
        mod = self.compile(schema)
        f = mod.Foo.from_buffer('somedata', 0, 0, 1)
        py.test.raises(ValueError, "f.x")

    def test_anyPointer_null(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            x @0 :AnyPointer;
        }
        """
        mod = self.compile(schema)
        f = mod.Foo.from_buffer('', 0, data_size=0, ptrs_size=0)
        assert f.x is None


class TestList(CompilerTest):

    def test_list_of_primitive(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            items @0 :List(Int64);
        }
        """
        mod = self.compile(schema)
        buf = ('\x01\x00\x00\x00\x25\x00\x00\x00'   # ptrlist
               '\x01\x00\x00\x00\x00\x00\x00\x00'   # 1
               '\x02\x00\x00\x00\x00\x00\x00\x00'   # 2
               '\x03\x00\x00\x00\x00\x00\x00\x00'   # 3
               '\x04\x00\x00\x00\x00\x00\x00\x00')  # 4
        f = mod.Foo.from_buffer(buf, 0, 0, 1)
        assert f.items == [1, 2, 3, 4]

    def test_list_of_void(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            items @0 :List(Void);
        }
        """
        mod = self.compile(schema)
        buf = ('\x01\x00\x00\x00\x20\x00\x00\x00')   # ptrlist
        f = mod.Foo.from_buffer(buf, 0, 0, 1)
        assert len(f.items) == 4
        assert list(f.items) == [None]*4


    def test_list_of_structs(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Polygon {
            struct Point {
                x @0 :Int64;
                y @1 :Int64;
            }
            points @0 :List(Point);
        }
        """
        mod = self.compile(schema)
        buf = ('\x01\x00\x00\x00\x47\x00\x00\x00'    # ptrlist
               '\x10\x00\x00\x00\x02\x00\x00\x00'    # list tag
               '\x0a\x00\x00\x00\x00\x00\x00\x00'    # 10
               '\x64\x00\x00\x00\x00\x00\x00\x00'    # 100
               '\x14\x00\x00\x00\x00\x00\x00\x00'    # 20
               '\xc8\x00\x00\x00\x00\x00\x00\x00'    # 200
               '\x1e\x00\x00\x00\x00\x00\x00\x00'    # 30
               '\x2c\x01\x00\x00\x00\x00\x00\x00'    # 300
               '\x28\x00\x00\x00\x00\x00\x00\x00'    # 40
               '\x90\x01\x00\x00\x00\x00\x00\x00')   # 400
        poly = mod.Polygon.from_buffer(buf, 0, 0, 1)
        assert len(poly.points) == 4
        assert poly.points[0].x == 10
        assert poly.points[0].y == 100

    def test_list_of_enum(self):
        schema = """
        @0xbf5147cbbecf40c1;
        enum Color {
           red @0;
           green @1;
           blue @2;
           yellow @3;
        }
        struct Flag {
            stripes @0 :List(Color);
        }
        """
        mod = self.compile(schema)
        buf = ('\x01\x00\x00\x00\x23\x00\x00\x00'    # ptrlist
               '\x00\x00\x01\x00\x02\x00\x03\x00')   # [0, 1, 2, 3]
        flag = mod.Flag.from_buffer(buf, 0, data_size=0, ptrs_size=1)
        assert len(flag.stripes) == 4
        assert list(flag.stripes) == [0, 1, 2, 3]
        colors = [str(x) for x in flag.stripes]
        assert colors == ['red', 'green', 'blue', 'yellow']

    def test_list_of_bool(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            items @0 :List(Bool);
        }
        """
        mod = self.compile(schema)
        buf = ('\x01\x00\x00\x00\x51\x00\x00\x00'    # ptrlist
               '\x2b\x02\x00\x00\x00\x00\x00\x00')
        f = mod.Foo.from_buffer(buf, 0, 0, 1)
        assert list(f.items) == [True, True, False, True, False, True, False, False,
                                 False, True]

    def test_list_of_text(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            items @0 :List(Text);
        }
        """
        mod = self.compile(schema)
        buf = ('\x01\x00\x00\x00\x1e\x00\x00\x00'    # ptrlist
               '\x09\x00\x00\x00\x22\x00\x00\x00'
               '\x09\x00\x00\x00\x22\x00\x00\x00'
               '\x09\x00\x00\x00\x22\x00\x00\x00'
               'foo\x00\x00\x00\x00\x00'
               'bar\x00\x00\x00\x00\x00'
               'baz\x00\x00\x00\x00\x00')
        f = mod.Foo.from_buffer(buf, 0, 0, 1)
        assert list(f.items) == ['foo', 'bar', 'baz']

    def test_list_of_data(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            items @0 :List(Data);
        }
        """
        mod = self.compile(schema)
        buf = ('\x01\x00\x00\x00\x1e\x00\x00\x00'  # ptrlist
               '\x09\x00\x00\x00\x1a\x00\x00\x00'
               '\x09\x00\x00\x00\x1a\x00\x00\x00'
               '\x09\x00\x00\x00\x1a\x00\x00\x00'
               'foo\x00\x00\x00\x00\x00'
               'bar\x00\x00\x00\x00\x00'
               'baz\x00\x00\x00\x00\x00')
        f = mod.Foo.from_buffer(buf, 0, 0, 1)
        assert list(f.items) == ['foo', 'bar', 'baz']

    def test_list_of_list(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            items @0 :List(List(Int8));
        }
        """
        mod = self.compile(schema)
        buf = ('\x01\x00\x00\x00\x1e\x00\x00\x00'   # list<ptr> (3 items)
               '\x09\x00\x00\x00\x1a\x00\x00\x00'   # list<8> (3 items)
               '\x09\x00\x00\x00\x12\x00\x00\x00'   # list<8> (2 items)
               '\x09\x00\x00\x00\x22\x00\x00\x00'   # list<8> (4 items)
               '\x01\x02\x03\x00\x00\x00\x00\x00'
               '\x04\x05\x00\x00\x00\x00\x00\x00'
               '\x06\x07\x08\x09\x00\x00\x00\x00')

        f = mod.Foo.from_buffer(buf, 0, 0, 1)
        lst = [list(item) for item in f.items]
        assert lst == [[1, 2, 3],
                       [4, 5],
                       [6, 7, 8, 9]]

