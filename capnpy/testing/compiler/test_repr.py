# -*- encoding: utf-8 -*-

import py
import pytest
from six import PY3, b

import capnpy
from capnpy.testing.compiler.support import CompilerTest


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
        res = stdout.strip()
        return res.decode('utf-8')

    def encode(self, cls, myrepr):
        from subprocess import Popen, PIPE
        cmd = ['capnp', 'encode', self.mod.__schema__, cls.__name__]
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        proc.stdin.write(myrepr.encode('utf-8'))
        stdout, stderr = proc.communicate()
        ret = proc.wait()
        if ret != 0:
            raise ValueError(stderr)
        res = stdout.strip()
        return cls.loads(res)

    def check(self, obj, expected, check_decode=True):
        myrepr = obj.shortrepr()
        assert myrepr == expected, 'shortrepr() is not what we expect'
        #
        if check_decode:
            # do not attempt to guarantee consistency with capnpy decode output
            # for data fields which is not even itself internally consistent
            capnp_repr = self.decode(obj)
            assert myrepr == capnp_repr, 'shortrepr() does not match with capnp decode'
        #
        new_obj = self.encode(obj.__class__, myrepr)
        assert obj.dumps() == new_obj.dumps(), 'shortrepr() failed to generate an equivalent object'

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
        self.check(p, u'(txt = "hellò")')

    def test_text_type_unicode(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct P {
            txt @0 :Text;
        }
        """
        self.mod = self.compile(schema, text_type='unicode')
        p = self.mod.P(txt=u'double "quotes"')
        self.check(p, r'(txt = "double \"quotes\"")')
        #
        p = self.mod.P(txt=u"single 'quotes'")
        self.check(p, r'(txt = "single \'quotes\'")')
        #
        p = self.mod.P(txt=u"tricky \" '")
        self.check(p, r'(txt = "tricky \" \'")')
        #
        p = self.mod.P(txt=u'hellò')
        self.check(p, u'(txt = "hellò")')

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
        self.check(p, u'(data = "hell\\xc3\\xb2")', check_decode=False)

    def test_data_non_textual(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct P {
            data @0 :Data;
        }
        """
        self.mod = self.compile(schema)
        p = self.mod.P(data=b'\xa3')
        self.check(p, r'(data = "\xa3")', check_decode=False)
        #
        p = self.mod.P(data=b'\x00')
        self.check(p, r'(data = "\x00")', check_decode=False)

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
        using Py = import "/capnpy/annotate.capnp";
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
        }
        struct P {
            ints @0 :List(Int64);
            structs @1 :List(Point);
            texts @2 :List(Text);
            unicodes @3 :List(Text) $Py.options(textType=unicode);
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
        #
        p = self.mod.P(ints=None, structs=None, unicodes=[u'hellò'])
        self.check(p, u'(unicodes = ["hellò"])')


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
                '\x00\x00\x00\x00\x02\x00\x00\x00'  # struct
                '\x00\x00\x00\x00\x00\x00\x00\x00'  # null ptr
                '\x00\x00\x00\x00\x00\x00\x00\x00') # null ptr
        p = self.mod.P.from_buffer(buf, 0, 1, 1)
        assert p.is_b()
        self.check(p, '(b = (x = 0, y = 0))')
        #
        buf = b('\x02\x00\x00\x00\x00\x00\x00\x00'  # tag == c
                '\x01\x00\x00\x00\x0a\x00\x00\x00'  # text
                '\x00\x00\x00\x00\x00\x00\x00\x00') # null ptr
        p = self.mod.P.from_buffer(buf, 0, 1, 1)
        assert p.is_c()
        self.check(p, '(c = "")')
        #
        buf = b('\x03\x00\x00\x00\x00\x00\x00\x00'  # tag == d
                '\x01\x00\x00\x00\x05\x00\x00\x00') # list
        p = self.mod.P.from_buffer(buf, 0, 1, 1)
        assert p.is_d()
        self.check(p, '(d = [])')

    def test_convert_case(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            fieldOne @0 :Int64;
            fieldTwo @1 :Int64;
        }
        """
        self.mod = self.compile(schema)
        p = self.mod.Foo(1, 2)
        # the shortrepr() always uses camelCase even if the attributes use python_case
        assert p.field_one == 1
        assert p.field_two == 2
        self.check(p, '(fieldOne = 1, fieldTwo = 2)')
        assert repr(p) == '<Foo: (fieldOne = 1, fieldTwo = 2)>'

    def test_nullable(self):
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
        self.check(foo, '(x = (isNull = 1, value = 0))')
        foo = self.mod.Foo(2)
        self.check(foo, '(x = (isNull = 0, value = 2))')
