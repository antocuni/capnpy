import py
import pytest
import capnpy
from capnpy.compiler import Compiler
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


class TestShortRepr(CompilerTest):

    def decode(self, obj):
        from capnpy.message import dumps
        from subprocess import Popen, PIPE
        cmd = ['capnp', 'decode', '--short', self.mod.__file__, obj.__class__.__name__]
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        proc.stdin.write(dumps(obj))
        stdout, stderr = proc.communicate()
        ret = proc.wait()
        if ret != 0:
            raise ValueError(stderr)
        return stdout.strip()

    def check(self, obj, expected=None):
        myrepr = obj.shortrepr()
        if expected is not None:
            assert myrepr == expected
        capnp_repr = self.decode(obj)
        assert myrepr == capnp_repr

    def test_primitive(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0 :Int64;
            y @1 :Float64;
        }
        """
        self.mod = self.compile(schema)
        p = self.mod.Point(1, 1.23)
        self.check(p, '(x = 1, y = 1.23)')

    def test_text(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Person {
            name @0 :Text;
            surname @1 :Text;
        }
        """
        self.mod = self.compile(schema)
        p = self.mod.Person(name=None, surname=None)
        self.check(p, '()')
        #
        p = self.mod.Person(name="foo", surname=None)
        self.check(p, '(name = "foo")')
        #
        p = self.mod.Person(name=None, surname="bar")
        self.check(p, '(surname = "bar")')
        #
        p = self.mod.Person(name="foo", surname='bar with "quotes"')
        self.check(p, r'(name = "foo", surname = "bar with \"quotes\"")')
