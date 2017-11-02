# -*- encoding: utf-8 -*-

import py
import pytest
from six import PY3, b

import capnpy
from capnpy.testing.compiler.support import CompilerTest
from capnpy.util import ensure_unicode


class TestShortRepr(CompilerTest):

    def decode(self, obj):
        from capnpy.message import dumps
        from subprocess import Popen, PIPE
        cmd = ['capnp', 'decode', '--short', self.mod.__schema__, obj.__class__.__name__]
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        proc.stdin.write(dumps(obj))
        stdout, stderr = proc.communicate()
        ret = proc.wait()
        if ret != 0:
            raise ValueError(stderr)
        return ensure_unicode(stdout.strip())

    def check(self, obj, expected=None):
        myrepr = obj.shortrepr()
        capnp_repr = self.decode(obj)
        assert myrepr == capnp_repr
        if expected is not None:
            assert myrepr == expected

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
        assert repr(p) == '<Point: (x = 1, y = 1.23)>'

    def test_bool(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct P {
            x @0 :Bool;
            y @1 :Bool;
        }
        """
        self.mod = self.compile(schema)
        buf = b'\x01\x00\x00\x00\x00\x00\x00\x00'
        p = self.mod.P.from_buffer(buf, 0, 1, 0)
        self.check(p, '(x = true, y = false)')

    def test_enum(self):
        schema = """
        @0xbf5147cbbecf40c1;
        enum Color {
            red @0;
            green @1;
            blue @2;
        }
        struct P {
            x @0 :Color;
            y @1 :Color;
        }
        """
        self.mod = self.compile(schema)
        buf = b'\x01\x00\x00\x00\x00\x00\x00\x00'
        p = self.mod.P.from_buffer(buf, 0, 1, 0)
        self.check(p, '(x = green, y = red)')

    def test_void(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0 :Int64;
            y @1 :Void;
        }
        """
        self.mod = self.compile(schema)
        p = self.mod.Point(1)
        self.check(p, '(x = 1, y = void)')

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
        p = self.mod.Person(name=b"foo", surname=None)
        self.check(p, '(name = "foo")')
        #
        p = self.mod.Person(name=None, surname=b"bar")
        self.check(p, '(surname = "bar")')
        #
        p = self.mod.Person(name=b"foo", surname=b"bar")
        self.check(p, '(name = "foo", surname = "bar")')

    def test_text_special_chars(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct P {
            txt @0 :Text;
        }
        """
        self.mod = self.compile(schema)
        p = self.mod.P(txt=b'double "quotes"')
        self.check(p, r'(txt = "double \"quotes\"")')
        #
        p = self.mod.P(txt=b"single 'quotes'")
        self.check(p, r'(txt = "single \'quotes\'")')
        #
        p = self.mod.P(txt=b"tricky \" '")
        self.check(p, r'(txt = "tricky \" \'")')
        #
        p = self.mod.P(txt=u'hellò'.encode('utf-8'))
        self.check(p, r'(txt = "hell\xc3\xb2")')

    def test_data_special_chars(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct P {
            data @0 :Data;
        }
        """
        self.mod = self.compile(schema)
        p = self.mod.P(data=b'double "quotes"')
        self.check(p, r'(data = "double \"quotes\"")')
        #
        p = self.mod.P(data=b"single 'quotes'")
        self.check(p, r'(data = "single \'quotes\'")')
        #
        p = self.mod.P(data=b"tricky \" '")
        self.check(p, r'(data = "tricky \" \'")')
        #
        p = self.mod.P(data=u'hellò'.encode('utf-8'))
        self.check(p, r'(data = "hell\xc3\xb2")')

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
            empty @2 :Point;
        }
        """
        self.mod = self.compile(schema)
        p1 = self.mod.Point(1, 2)
        p2 = self.mod.Point(3, 4)
        r = self.mod.Rectangle(p1, p2, None)
        self.check(r, '(a = (x = 1, y = 2), b = (x = 3, y = 4))')

    def test_list(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
        }
        struct P {
            ints @0 :List(Int64);
            structs @1 :List(Point);
            texts @2 :List(Text);
        }
        """
        self.mod = self.compile(schema)
        p = self.mod.P(ints=[1, 2, 3], structs=None, texts=None)
        self.check(p, '(ints = [1, 2, 3])')
        #
        p1 = self.mod.Point(1, 2)
        p2 = self.mod.Point(3, 4)
        p = self.mod.P(ints=None, structs=[p1, p2], texts=None)
        self.check(p, '(structs = [(x = 1, y = 2), (x = 3, y = 4)])')
        #
        p = self.mod.P(ints=None, structs=None, texts=[b'foo', b'bar', b'baz'])
        self.check(p, '(texts = ["foo", "bar", "baz"])')

    def test_list_of_bool(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            items @0 :List(Bool);
        }
        """
        self.mod = self.compile(schema)
        # at the moment of writing, List(Bool) is not supported by ctors, so
        # we create one from the buffer
        buf = b('\x01\x00\x00\x00\x19\x00\x00\x00'    # ptrlist
                '\x03\x00\x00\x00\x00\x00\x00\x00')
        f = self.mod.Foo.from_buffer(buf, 0, 0, 1)
        self.check(f, "(items = [true, true, false])")

    def test_group(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct P {
            foo :group {
                x @0 :Int64;
                y @1 :Int64;
            }
        }
        """
        self.mod = self.compile(schema)
        buf = b('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
                '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
        p = self.mod.P.from_buffer(buf, 0, 2, 0)
        self.check(p, '(foo = (x = 1, y = 2))')

    def test_union(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct P {
            union {
                x @0 :Int64;
                y @1 :Void;
                z @2 :Text;
            }
        }
        """
        self.mod = self.compile(schema)
        p = self.mod.P.new_x(1)
        self.check(p, '(x = 1)')
        #
        p = self.mod.P.new_y()
        self.check(p, '(y = void)')
        #
        p = self.mod.P.new_z(b'hello')
        self.check(p, '(z = "hello")')

    def test_union_set_but_null_pointer(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
        }
        struct P {
            union {
                a @0 :Point;
                b @1 :Point;
                c @2 :Text;
                d @3 :List(Int64);
            }
        }
        """
        self.mod = self.compile(schema)
        buf = b('\x00\x00\x00\x00\x00\x00\x00\x00'  # tag == a
                '\x00\x00\x00\x00\x00\x00\x00\x00') # null ptr
        p = self.mod.P.from_buffer(buf, 0, 1, 1)
        assert p.is_a()
        self.check(p, '()') # the default value is always empty
        #
        buf = b('\x01\x00\x00\x00\x00\x00\x00\x00'  # tag == b
                '\x00\x00\x00\x00\x00\x00\x00\x00') # null ptr
        p = self.mod.P.from_buffer(buf, 0, 1, 1)
        assert p.is_b()
        self.check(p, '(b = (x = 0, y = 0))')
        #
        buf = b('\x02\x00\x00\x00\x00\x00\x00\x00'  # tag == c
                '\x00\x00\x00\x00\x00\x00\x00\x00') # null ptr
        p = self.mod.P.from_buffer(buf, 0, 1, 1)
        assert p.is_c()
        self.check(p, '(c = "")')
        #
        buf = b('\x03\x00\x00\x00\x00\x00\x00\x00'  # tag == d
                '\x00\x00\x00\x00\x00\x00\x00\x00') # null ptr
        p = self.mod.P.from_buffer(buf, 0, 1, 1)
        assert p.is_d()
        self.check(p, '(d = [])')

    def test_null(self):
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
        self.mod = self.compile(schema)
        foo = self.mod.Foo(None)
        assert foo.shortrepr() == '(x = None)'
        foo = self.mod.Foo(2)
        assert foo.shortrepr() == '(x = 2)'
