import py
import six
from six import b

from capnpy.testing.compiler.support import CompilerTest

class TestNullPointers(CompilerTest):

    @py.test.fixture
    def mod(self):
        schema = """
        @0xbf5147cbbecf40c1;
        using Py = import "/capnpy/annotate.capnp";
        struct P {
            a @0 :Int64;
            b @1 :Int64;
        }

        struct Foo {
            x @0 :Text;
            y @1 :List(Int64);
            z @2 :P;
            u @3 :Text $Py.options(textType=unicode);
        }
        """
        return self.compile(schema)

    def test_null_pointers(self, mod):
        buf = b('\x00\x00\x00\x00\x00\x00\x00\x00'   # null
                '\x00\x00\x00\x00\x00\x00\x00\x00'   # null
                '\x00\x00\x00\x00\x00\x00\x00\x00'   # null
                '\x00\x00\x00\x00\x00\x00\x00\x00')  # null
        f = mod.Foo.from_buffer(buf, 0, data_size=0, ptrs_size=3)
        assert f.x is None
        assert f.y is None
        assert f.z is None
        assert f.u is None
        assert not f.has_x()
        assert not f.has_y()
        assert not f.has_z()
        assert not f.has_u()

    def test_get_methods(self, mod):
        buf = b('\x00\x00\x00\x00\x00\x00\x00\x00'   # null
                '\x00\x00\x00\x00\x00\x00\x00\x00'   # null
                '\x00\x00\x00\x00\x00\x00\x00\x00'   # null
                '\x00\x00\x00\x00\x00\x00\x00\x00')  # null
        f = mod.Foo.from_buffer(buf, 0, data_size=0, ptrs_size=3)
        assert f.x is None
        assert f.get_x() == b''
        assert type(f.get_x()) is bytes
        #
        assert f.y is None
        assert f.get_y() == []
        #
        assert f.z is None
        assert f.get_z().a == 0
        assert f.get_z().b == 0
        #
        assert f.u is None
        assert f.get_u() == u''
        assert type(f.get_u()) is six.text_type

    def test_default_when_null(self, mod):
        buf = b''
        f = mod.Foo.from_buffer(buf, 0, data_size=0, ptrs_size=0)
        assert f.x is None
        assert f.y is None
        assert f.z is None
        assert f.u is None
        assert not f.has_x()
        assert not f.has_y()
        assert not f.has_z()
        assert not f.has_u()

    def test_nonnull(self, mod):
        # now with non-null ptrs
        buf = b('\x01\x00\x00\x00\x02\x00\x00\x00'   # non-null empty list, size=8
                '\x01\x00\x00\x00\x05\x00\x00\x00'   # non-null empty list, size=64
                '\xfc\xff\xff\xff\x00\x00\x00\x00')  # non-null empty struct
        f = mod.Foo.from_buffer(buf, 0, data_size=0, ptrs_size=3)
        assert f.x == b''
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
                isNull @0 :Bool;
                value  @1 :Int64;
            }
        }
        struct Bar {
            point :group $Py.nullable {
                isNull @0 :Int8;
                value :group {
                    x @1: Int8;
                    y @2: Int8;
                }
            }
        }
        """
        return self.compile(schema)

    def test_nullable(self, mod):
        buf = b('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
                '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
        foo = mod.Foo.from_buffer(buf, 0, 2, 0)
        assert foo._x.is_null
        assert foo._x.value == 2
        assert foo.x is None
        #
        buf = b('\x00\x00\x00\x00\x00\x00\x00\x00'  # 0
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
        #
        foo = mod.Foo()
        assert not foo._x.is_null
        assert foo._x.value == 0
        assert foo.x == 0

    def test_ctor_nullable_group(self, mod):
        # check that we can pass a null value
        bar = mod.Bar(point=None)
        assert bar._point.is_null
        assert bar.point is None
        #
        # check that we can pass a non-null value
        bar = mod.Bar(point=(1,2))
        assert not bar._point.is_null
        assert bar._point.value.x == 1
        assert bar._point.value.y == 2
        assert bar.point.x == 1
        assert bar.point.y == 2
        #
        # check that we can use the ctor-like syntax
        bar = mod.Bar(mod.Bar_point.Value(x=1, y=2))
        assert bar.point.x == 1
        assert bar.point.y == 2

    def test_bad_nullable(self):
        schema = """
        @0xbf5147cbbecf40c1;
        using Py = import "/capnpy/annotate.capnp";
        struct Foo {
            x :group $Py.nullable {
                wrongName @0 :Bool;
                value  @1 :Int64;
            }
        }
        """
        exc = py.test.raises(ValueError, "self.compile(schema)")
        msg = str(exc.value)
        assert msg == ('x: nullable groups must have exactly two fields: '
                       '"isNull" and "value"')

    def test_bad_nullable_2(self):
        schema = """
        @0xbf5147cbbecf40c1;
        using Py = import "/capnpy/annotate.capnp";
        struct Foo {
            x :group $Py.nullable {
                isNull @0 :Int8;
                value  @1 :Text;
            }
        }
        """
        exc = py.test.raises(ValueError, "self.compile(schema)")
        msg = str(exc.value)
        assert msg == ('x: cannot use pointer types for nullable values. '
                       'Pointers are already nullable.')

    def test_default_nonnull(self):
        schema = """
        @0xbf5147cbbecf40c1;
        using Py = import "/capnpy/annotate.capnp";
        struct Foo {
            x :group $Py.nullable {
                isNull @0 :Bool;
                value  @1 :Int64 = 42;
            }
        }
        """
        mod = self.compile(schema)
        foo = mod.Foo()
        assert foo.x == 42
        assert foo._seg.buf == b(
            '\x00\x00\x00\x00\x00\x00\x00\x00'  # 0
            '\x00\x00\x00\x00\x00\x00\x00\x00') # 0 (value == 42)

    def test_default_nonnull_group(self):
        schema = """
        @0xbf5147cbbecf40c1;
        using Py = import "/capnpy/annotate.capnp";
        struct Foo {
            point :group $Py.nullable {
                isNull @0 :Bool;
                value :group {
                    x @1: Int8 = 4;
                    y @2: Int8 = 5;
                    z @3: Int8 = 6;
                }
            }
        }
        """
        mod = self.compile(schema)
        foo = mod.Foo()
        assert foo.point.x == 4
        assert foo.point.y == 5
        assert foo.point.z == 6
        assert foo._seg.buf == b('\x00\x00\x00\x00\x00\x00\x00\x00')

    def test_default_null(self):
        schema = """
        @0xbf5147cbbecf40c1;
        using Py = import "/capnpy/annotate.capnp";
        struct Foo {
            x :group $Py.nullable {
                isNull @0 :Bool = true;
                value  @1 :Int64;
            }
        }
        """
        mod = self.compile(schema)
        foo = mod.Foo()
        assert foo.x is None
        assert foo._seg.buf == b(
            '\x00\x00\x00\x00\x00\x00\x00\x00'  # 0 (isNull == true)
            '\x00\x00\x00\x00\x00\x00\x00\x00') # 0

    def test_default_null_group(self):
        schema = """
        @0xbf5147cbbecf40c1;
        using Py = import "/capnpy/annotate.capnp";
        struct Foo {
            point :group $Py.nullable {
                isNull @0 :Bool = true;
                value :group {
                    x @1: Int8;
                    y @2: Int8;
                    z @3: Int8;
                }
            }
        }
        """
        mod = self.compile(schema)
        foo = mod.Foo()
        assert foo.point is None
        assert foo._seg.buf == b('\x00\x00\x00\x00\x00\x00\x00\x00')
