# -*- encoding: utf-8 -*-
import py
from six import b
from capnpy.list import PrimitiveItemType, StructItemType
from capnpy.type import Types
from capnpy.testing.compiler.support import CompilerTest

class TestAnyPointer(CompilerTest):

    def test_null(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            x @0 :AnyPointer;
        }
        """
        mod = self.compile(schema)
        f = mod.Foo.from_buffer(b'', 0, data_size=0, ptrs_size=0)
        assert f.x is None

    def test_as_text(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            p @0 :AnyPointer;
        }
        """
        mod = self.compile(schema)
        buf = b('\x01\x00\x00\x00\x82\x00\x00\x00'  # ptrlist
                'h\xc3\xa0lo capnproto\x00')         # utf-8 text
        f = mod.Foo.from_buffer(buf, 0, 0, 1)
        p = f.p
        assert not p.is_struct()
        assert p.is_list()
        assert p.is_text()
        assert p.is_data()
        assert p.as_text_bytes() == b'h\xc3\xa0lo capnproto'
        assert p.as_text_unicode() == u'hàlo capnproto'
        assert p.as_data() == b'h\xc3\xa0lo capnproto\0'

    def test_as_struct(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
        }
        struct Rectangle {
            a @0 :AnyPointer;
            b @1 :AnyPointer;
        }
        """
        mod = self.compile(schema)
        buf = b('\x04\x00\x00\x00\x02\x00\x00\x00'    # ptr to a
                '\x08\x00\x00\x00\x02\x00\x00\x00'    # ptr to b
                '\x01\x00\x00\x00\x00\x00\x00\x00'    # a.x == 1
                '\x02\x00\x00\x00\x00\x00\x00\x00'    # a.y == 2
                '\x03\x00\x00\x00\x00\x00\x00\x00'    # b.x == 3
                '\x04\x00\x00\x00\x00\x00\x00\x00')   # b.y == 4
        r = mod.Rectangle.from_buffer(buf, 0, 0, 2)
        assert r.a.is_struct()
        assert not r.a.is_list()
        assert not r.a.is_text()
        p1 = r.a.as_struct(mod.Point)
        p2 = r.b.as_struct(mod.Point)
        assert p1.x == 1
        assert p1.y == 2
        assert p2.x == 3
        assert p2.y == 4

    def test_as_list_of_primitives(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            p @0 :AnyPointer;
        }
        """
        mod = self.compile(schema)
        buf = b('\x01\x00\x00\x00\x25\x00\x00\x00'   # ptrlist
                '\x01\x00\x00\x00\x00\x00\x00\x00'   # 1
                '\x02\x00\x00\x00\x00\x00\x00\x00'   # 2
                '\x03\x00\x00\x00\x00\x00\x00\x00'   # 3
                '\x04\x00\x00\x00\x00\x00\x00\x00')  # 4
        f = mod.Foo.from_buffer(buf, 0, 0, 1)
        assert f.p.is_list()
        assert not f.p.is_struct()
        assert not f.p.is_text()
        items = f.p.as_list(PrimitiveItemType(Types.int64))
        assert items == [1, 2, 3, 4]
        #
        # automatically construct the appropriate ItemType
        items = f.p.as_list(int)
        assert items == [1, 2, 3, 4]

    def test_as_list_of_structs(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Polygon {
            struct Point {
                x @0 :Int64;
                y @1 :Int64;
            }
            points @0 :AnyPointer;
        }
        """
        mod = self.compile(schema)
        buf = b('\x01\x00\x00\x00\x47\x00\x00\x00'    # ptrlist
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
        assert poly.points.is_list()
        assert not poly.points.is_struct()
        assert not poly.points.is_text()
        points = poly.points.as_list(StructItemType(mod.Polygon_Point))
        assert len(points) == 4
        assert points[0].x == 10
        assert points[0].y == 100
        #
        points = poly.points.as_list(mod.Polygon_Point)
        assert len(points) == 4
        assert points[0].x == 10
        assert points[0].y == 100

    def test_dumps(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
        }
        struct Foo1 {
            p @0 :Point;
        }
        struct Foo2 {
            anyp @0 :AnyPointer;
        }
        """
        mod = self.compile(schema)
        a = mod.Foo1(mod.Point(1, 2))
        b = mod.Foo2.loads(a.dumps())
        assert a.p.dumps() == b.anyp.dumps()
