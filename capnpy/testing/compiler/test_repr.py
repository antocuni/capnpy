import py
import pytest
import capnpy
from capnpy.testing.compiler.support import CompilerTest


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
