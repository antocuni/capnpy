import py
import pytest
import capnpy
from capnpy.testing.compiler.support import CompilerTest


class TestCompilerOptions(CompilerTest):
    
    def test_convert_case_fields(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct MyStruct {
            firstAttr @0 :Int64;
            secondAttr @1 :Int64;
        }
        """
        mod = self.compile(schema)
        assert hasattr(mod.MyStruct, 'first_attr')
        assert hasattr(mod.MyStruct, 'second_attr')

    def test_no_convert_case(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct MyStruct {
            firstAttr @0 :Int64;
            secondAttr @1 :Int64;
        }
        """
        mod = self.compile(schema, convert_case=False)
        assert hasattr(mod.MyStruct, 'firstAttr')
        assert hasattr(mod.MyStruct, 'secondAttr')

    def test_convert_case_enum(self):
        schema = """
        @0xbf5147cbbecf40c1;
        enum Foo {
            firstItem @0;
            secondItem @1;
        }
        """
        mod = self.compile(schema)
        assert mod.Foo.first_item == 0
        assert mod.Foo.second_item == 1


    def test_name_clash(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Types {
        }
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
        }
        """
        mod = self.compile(schema)
        #
        buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
               '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
        p = mod.Point.from_buffer(buf, 0, 2, 0)
        assert p.x == 1
        assert p.y == 2

    def test_keyword_as_fieldname(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct P {
            def @0 :Int64;
            if @1 :Int64;
        }
        """
        mod = self.compile(schema)
        #
        buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
               '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
        p = mod.P.from_buffer(buf, 0, 2, 0)
        assert p.def_ == 1
        assert p.if_ == 2

    def test_c_type_as_fieldname(self):
        # this used to fail in pyx mode
        schema = """
        @0xbf5147cbbecf40c1;
        struct P {
            void @0 :Int64;
            int @1 :Int64;
        }
        """
        mod = self.compile(schema)
        #
        buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
               '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
        p = mod.P.from_buffer(buf, 0, 2, 0)
        assert p.void == 1
        assert p.int == 2

    def test_c_type_as_fieldname_union(self):
        # this used to fail in pyx mode
        schema = """
        @0xbf5147cbbecf40c1;
        struct P {
            union {
                void @0 :Int64;
                int @1 :Int64;
            }
        }
        """
        mod = self.compile(schema)
        #
        buf = ('\x2a\x00\x00\x00\x00\x00\x00\x00'  # 42
               '\x01\x00\x00\x00\x00\x00\x00\x00') # tag == int
        p = mod.P.from_buffer(buf, 0, 2, 0)
        assert p.is_int()
        assert p.int == 42

    def test_nested_struct(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Outer {
            struct Point {
                x @0 :Int64;
                y @1 :Int64;
            }
        }
        """
        mod = self.compile(schema)
        #
        buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
               '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
        p = mod.Outer.Point.from_buffer(buf, 0, 2, 0)
        assert p.x == 1
        assert p.y == 2
        #
        assert not hasattr(mod, 'Outer_Point')
        if not self.pyx:
            # unfortunately, the nice dotted name works only in pure Python
            assert mod.Outer.Point.__name__ == 'Outer.Point'

    def test_const(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            const bar :UInt16 = 42;
        }
        """
        mod = self.compile(schema)
        assert mod.Foo.bar == 42

    def test_global_const(self):
        schema = """
        @0xbf5147cbbecf40c1;
        const bar :UInt16 = 42;
        """
        mod = self.compile(schema)
        assert mod.bar == 42
