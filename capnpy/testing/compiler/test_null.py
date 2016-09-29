import py
from capnpy.testing.compiler.support import CompilerTest

class TestNullPointers(CompilerTest):

    @py.test.fixture
    def mod(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct P {
            a @0 :Int64;
            b @1 :Int64;
        }

        struct Foo {
            x @0 :Text;
            y @1 :List(Int64);
            z @2 :P;
        }
        """
        return self.compile(schema)

    def test_null_pointers(self, mod):
        buf = ('\x00\x00\x00\x00\x00\x00\x00\x00'   # null
               '\x00\x00\x00\x00\x00\x00\x00\x00'   # null
               '\x00\x00\x00\x00\x00\x00\x00\x00')  # null
        f = mod.Foo.from_buffer(buf, 0, data_size=0, ptrs_size=3)
        assert f.x is None
        assert f.y is None
        assert f.z is None
        assert not f.has_x()
        assert not f.has_y()
        assert not f.has_z()

    def test_get_methods(self, mod):
        buf = ('\x00\x00\x00\x00\x00\x00\x00\x00'   # null
               '\x00\x00\x00\x00\x00\x00\x00\x00'   # null
               '\x00\x00\x00\x00\x00\x00\x00\x00')  # null
        f = mod.Foo.from_buffer(buf, 0, data_size=0, ptrs_size=3)
        assert f.x is None
        assert f.get_x() == ''
        #
        assert f.y is None
        assert f.get_y() == []
        #
        assert f.z is None
        assert f.get_z().a == 0
        assert f.get_z().b == 0

    def test_default_when_null(self, mod):
        buf = ''
        f = mod.Foo.from_buffer(buf, 0, data_size=0, ptrs_size=0)
        assert f.x is None
        assert f.y is None
        assert f.z is None
        assert not f.has_x()
        assert not f.has_y()
        assert not f.has_z()

    def test_nonnull(self, mod):
        # now with non-null ptrs
        buf = ('\x01\x00\x00\x00\x02\x00\x00\x00'   # non-null empty list, size=8
               '\x01\x00\x00\x00\x05\x00\x00\x00'   # non-null empty list, size=64
               '\xfc\xff\xff\xff\x00\x00\x00\x00')  # non-null empty struct
        f = mod.Foo.from_buffer(buf, 0, data_size=0, ptrs_size=3)
        assert f.x == ''
        assert f.y == []
        assert f.z is not None and isinstance(f.z, mod.P)
        assert f.has_x()
        assert f.has_y()
        assert f.has_z()



class TestNullable(CompilerTest):

    @py.test.fixture
    def mod(self):
        schema = """
        @0xbf5147cbbecf40c1;
        using Py = import "/capnpy/annotate.capnp";
        struct Foo {
            x :group $Py.nullable {
                isNull @0 :Int8;
                value  @1 :Int64;
            }
        }
        """
        return self.compile(schema)

    def test_nullable(self, mod):
        buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
               '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
        foo = mod.Foo.from_buffer(buf, 0, 2, 0)
        assert foo._x.is_null
        assert foo._x.value == 2
        assert foo.x is None
        #
        buf = ('\x00\x00\x00\x00\x00\x00\x00\x00'  # 0
               '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
        foo = mod.Foo.from_buffer(buf, 0, 2, 0)
        assert not foo._x.is_null
        assert foo._x.value == 2
        assert foo.x == 2

    def test_constructor(self, mod):
        foo = mod.Foo(x=None)
        assert foo._x.is_null
        assert foo._x.value == 0
        assert foo.x is None
        #
        foo = mod.Foo(x=42)
        assert not foo._x.is_null
        assert foo._x.value == 42
        assert foo.x == 42

    def test_bad_nullable(self):
        schema = """
        @0xbf5147cbbecf40c1;
        using Py = import "/capnpy/annotate.capnp";
        struct Foo {
            x :group $Py.nullable {
                wrongName @0 :Int8;
                value  @1 :Int64;
            }
        }
        """
        exc = py.test.raises(ValueError, "self.compile(schema)")
        msg = str(exc.value)
        assert msg == ('x: nullable groups must have exactly two fields: '
                       '"isNull" and "value"')
