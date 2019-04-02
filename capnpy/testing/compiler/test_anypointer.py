import py
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
        buf = (b'\x01\x00\x00\x00\x82\x00\x00\x00'  # ptrlist
               'hello capnproto\0')                 # string
        f = mod.Foo.from_buffer(buf, 0, 0, 1)
        p = f.p
        assert not p.is_struct()
        assert p.is_list()
        assert p.is_text()
        assert p.is_data()
        assert p.as_text() == 'hello capnproto'
        assert p.as_data() == 'hello capnproto\0'

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
        buf = (b'\x04\x00\x00\x00\x02\x00\x00\x00'   # ptr to a
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
