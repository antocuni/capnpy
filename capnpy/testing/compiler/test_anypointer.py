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
        assert p.as_text() == 'hello capnproto'
