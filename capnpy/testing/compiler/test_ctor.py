import py
import pytest
from capnpy.schema import Field, Type, Value
from capnpy.compiler.structor import Structor, FieldTree
from capnpy.testing.compiler.support import CompilerTest

class TestConstructors(CompilerTest):

    def test_primitive(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
        }
        """
        mod = self.compile(schema)
        buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
               '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
        #
        p = mod.Point(1, 2)
        assert p.x == 1
        assert p.y == 2
        assert p._seg.buf == buf
        #
        p = mod.Point(y=2, x=1)
        assert p.x == 1
        assert p.y == 2
        assert p._seg.buf == buf

    def test_enum(self):
        schema = """
        @0xbf5147cbbecf40c1;
        enum Color {
            red @0;
            green @1;
            blue @2;
            yellow @3;
        }
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
            color @2 :Color;
        }
        """
        mod = self.compile(schema)
        buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
               '\x02\x00\x00\x00\x00\x00\x00\x00'  # 2
               '\x03\x00\x00\x00\x00\x00\x00\x00') # yellow
        #
        p = mod.Point(1, 2, mod.Color.yellow)
        assert p.x == 1
        assert p.y == 2
        assert p.color == mod.Color.yellow
        assert p._seg.buf == buf


    def test_order_of_arguments(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0 :Int8;
            y @1 :Int64;
            z @2 :Int8;
        }
        """
        mod = self.compile(schema)
        # note that the order of fields is different than the order of offsets
        # (because z has offset==1 and y offset==8)
        p = mod.Point(1, 2, 3)
        assert p.x == 1
        assert p.y == 2
        assert p.z == 3

    def test_void(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
            z @2 :Void;
        }
        """
        mod = self.compile(schema)
        buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
               '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
        #
        p = mod.Point(1, 2)
        assert p.x == 1
        assert p.y == 2
        assert p._seg.buf == buf
        py.test.raises(TypeError, "mod.Point(z=None)")

    def test_text(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            x @0 :Int64;
            y @1 :Text;
        }
        """
        mod = self.compile(schema)
        foo = mod.Foo(1, 'hello capnp')
        assert foo._seg.buf == ('\x01\x00\x00\x00\x00\x00\x00\x00'
                              '\x01\x00\x00\x00\x62\x00\x00\x00'
                              'h' 'e' 'l' 'l' 'o' ' ' 'c' 'a'
                              'p' 'n' 'p' '\x00\x00\x00\x00\x00')

    def test_data(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            x @0 :Int64;
            y @1 :Data;
        }
        """
        mod = self.compile(schema)
        foo = mod.Foo(1, 'hello capnp')
        assert foo._seg.buf == ('\x01\x00\x00\x00\x00\x00\x00\x00'
                              '\x01\x00\x00\x00\x5a\x00\x00\x00'
                              'h' 'e' 'l' 'l' 'o' ' ' 'c' 'a'
                              'p' 'n' 'p' '\x00\x00\x00\x00\x00')

    def test_struct(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
        }
        struct Foo {
            x @0 :Point;
        }
        """
        mod = self.compile(schema)
        p = mod.Point(1, 2)
        foo = mod.Foo(p)
        assert foo._seg.buf == ('\x00\x00\x00\x00\x02\x00\x00\x00'  # ptr to point
                                '\x01\x00\x00\x00\x00\x00\x00\x00'  # p.x == 1
                                '\x02\x00\x00\x00\x00\x00\x00\x00') # p.y == 2


    def test_list(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            x @0 :List(Int8);
        }
        """
        mod = self.compile(schema)
        foo = mod.Foo([1, 2, 3, 4])
        assert foo._seg.buf == ('\x01\x00\x00\x00\x22\x00\x00\x00'   # ptrlist
                              '\x01\x02\x03\x04\x00\x00\x00\x00')  # 1,2,3,4 + padding

    def test_list_of_void(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            x @0 :List(Void);
        }
        """
        mod = self.compile(schema)
        foo = mod.Foo([None]*4)
        assert foo._seg.buf == ('\x01\x00\x00\x00\x20\x00\x00\x00')  # ptrlist

    def test_list_of_text(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            x @0 :List(Text);
        }
        """
        mod = self.compile(schema)
        foo = mod.Foo(['foo', 'bar', 'baz'])
        expected = ('\x01\x00\x00\x00\x1e\x00\x00\x00'    # ptrlist
                    '\x09\x00\x00\x00\x22\x00\x00\x00'
                    '\x09\x00\x00\x00\x22\x00\x00\x00'
                    '\x09\x00\x00\x00\x22\x00\x00\x00'
                    'foo\x00\x00\x00\x00\x00'
                    'bar\x00\x00\x00\x00\x00'
                    'baz\x00\x00\x00\x00\x00')
        assert foo._seg.buf == expected

    def test_list_of_data(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            x @0 :List(Data);
        }
        """
        mod = self.compile(schema)
        foo = mod.Foo(['foo', 'bar', 'baz'])
        expected = ('\x01\x00\x00\x00\x1e\x00\x00\x00'    # ptrlist
                    '\x09\x00\x00\x00\x1a\x00\x00\x00'
                    '\x09\x00\x00\x00\x1a\x00\x00\x00'
                    '\x09\x00\x00\x00\x1a\x00\x00\x00'
                    'foo\x00\x00\x00\x00\x00'
                    'bar\x00\x00\x00\x00\x00'
                    'baz\x00\x00\x00\x00\x00')
        assert foo._seg.buf == expected

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
        p1 = mod.Polygon.Point(1, 2)
        p2 = mod.Polygon.Point(3, 4)
        poly = mod.Polygon([p1, p2])
        assert poly.points[0].x == 1
        assert poly.points[0].y == 2
        assert poly.points[1].x == 3
        assert poly.points[1].y == 4

    def test_list_of_lists(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            x @0 :List(List(Int8));
        }
        """
        mod = self.compile(schema)
        foo = mod.Foo([[1, 2, 3], [4, 5], [6, 7, 8, 9]])
        expected = ('\x01\x00\x00\x00\x1e\x00\x00\x00'  # list<ptr> (3 items)
                    '\x09\x00\x00\x00\x1a\x00\x00\x00'  # list<8> (3 items)
                    '\x09\x00\x00\x00\x12\x00\x00\x00'  # list<8> (2 items)
                    '\x09\x00\x00\x00\x22\x00\x00\x00'  # list<8> (4 items)
                    '\x01\x02\x03\x00\x00\x00\x00\x00'
                    '\x04\x05\x00\x00\x00\x00\x00\x00'
                    '\x06\x07\x08\x09\x00\x00\x00\x00')
        assert foo._seg.buf == expected


    def test_group(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Point {
            position :group {
                x @0 :Int64;
                y @1 :Int64;
            }
            color @2 :Text;
        }
        """
        mod = self.compile(schema)
        p = mod.Point(position=(1, 2), color='red')
        assert p.position.x == 1
        assert p.position.y == 2
        assert p.color == 'red'

    def test_nested_group(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Shape {
            position :group {
                a :group {
                    x @0 :Int64;
                    y @1 :Int64;
                }
                b :group {
                    x @2 :Int64;
                    y @3 :Int64;
                }
            }
        }
        """
        mod = self.compile(schema)
        p = mod.Shape(position=((1, 2), (3, 4)))
        assert p.position.a.x == 1
        assert p.position.a.y == 2
        assert p.position.b.x == 3
        assert p.position.b.y == 4

    def test_group_named_params(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Point {
            position :group {
                x @0 :Int64;
                y @1 :Int64;
            }
            color :group {
                alpha @2 :Float64;
                name  @3 :Text;
            }
        }
        """
        mod = self.compile(schema)
        p = mod.Point(position=mod.Point.Position(x=1, y=2),
                      color=mod.Point.Color(alpha=1.0, name='red'))
        assert p.position.x == 1
        assert p.position.y == 2
        assert p.color.alpha == 1.0
        assert p.color.name == 'red'

    def test_group_void(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Point {
            position :group {
                x @0 :Int64;
                y @1 :Int64;
                empty @2 :Void;
            }
        }
        """
        mod = self.compile(schema)
        p = mod.Point(position=(1, 2))
        assert p.position.x == 1
        assert p.position.y == 2
        assert p.position.empty is None


class TestDefaults(CompilerTest):
    
    def test_no_args(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
        }
        """
        mod = self.compile(schema)
        p = mod.Point() # note that we are not passing any argument
        assert p.x == 0
        assert p.y == 0

    def test_explicit_default_primitive(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0 :Int64 = 42;
            y @1 :Int64;
        }
        """
        mod = self.compile(schema)
        p = mod.Point(0, 0)
        assert p.x == 0
        assert p.y == 0
        #
        p = mod.Point()
        assert p.x == 42
        assert p.y == 0

    def test_explicit_default_enum(self):
        schema = """
        @0xbf5147cbbecf40c1;
        enum Color {
            red @0;
            green @1;
            blue @2;
            yellow @3;
        }
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
            color @2 :Color = blue;
        }
        """
        mod = self.compile(schema)
        p = mod.Point(x=1, y=2, color=mod.Color.red)
        assert p.x == 1
        assert p.y == 2
        assert p.color == mod.Color.red == 0
        #
        p = mod.Point()
        assert p.x == 0
        assert p.y == 0
        assert p.color == mod.Color.blue == 2

    def test_group(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Point {
            position :group {
                x @0 :Int64 = 100;
                y @1 :Int64 = 200;
            }
        }
        """
        mod = self.compile(schema)
        p = mod.Point()
        assert p.position.x == 100
        assert p.position.y == 200

    def test_group_named_params(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Point {
            position :group {
                x @0 :Int64 = 42;
                y @1 :Int64;
            }
            color :group {
                alpha @2 :UInt8 = 255;
                name  @3 :Text;
            }
        }
        """
        mod = self.compile(schema)
        assert mod.Point.Position() == (42, 0)
        assert mod.Point.Color() == (255, None)
        p = mod.Point(position=mod.Point.Position(y=2),
                      color=mod.Point.Color(name='red'))
        assert p.position.x == 42
        assert p.position.y == 2
        assert p.color.alpha == 255
        assert p.color.name == 'red'

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
        f = mod.Foo(42, True, False, True)
        assert f.a
        assert not f.b
        assert f.c
        assert f.padding == 42
        #
        f = mod.Foo(42, False, True, False)
        assert not f.a
        assert f.b
        assert not f.c

    def test_bool_default(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            padding @0 :Int64;
            a @1 :Bool = true;
            b @2 :Bool = false;
            c @3 :Bool = true;
        }
        """
        mod = self.compile(schema)
        f = mod.Foo()
        assert f.a
        assert not f.b
        assert f.c

