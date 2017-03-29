"""
Integration tests which don't fit anywhere else :)
"""

import py
from capnpy.testing.compiler.support import CompilerTest

class TestIntegration(CompilerTest):

    def test_listbuilder_bug(self):
        schema = """
            @0xbf5147cbbecf40c1;
            struct Bar {
                x @0 :Int64;
                y @1 :Int64;
            }

            struct Foo {
                name @0 :Text;
                bars @1 :List(Bar);
            }
        """
        mod = self.compile(schema)
        bars = [mod.Bar(1, 2)]
        foo = mod.Foo('name', bars)
        assert len(foo.bars) == 1
        assert foo.bars[0].x == 1
        assert foo.bars[0].y == 2

    def test_listbuilder_null_ptrs(self):
        schema = """
            @0xbf5147cbbecf40c1;
            struct Bar {
                x @0 :Int64;
                y @1 :Int64;
                name @2 :Text;
            }

            struct Foo {
                bars @0 :List(Bar);
            }
        """
        mod = self.compile(schema)
        a = mod.Bar(1, 2, None)
        b = mod.Bar(3, 4, None)
        foo = mod.Foo([a, b])
        a1 = foo.bars[0]
        assert a1.x == 1
        assert a1.y == 2
        assert a1.name is None


    def test_compact_structs(self):
        schema = """
            @0xbf5147cbbecf40c1;
            struct Person {
                name @0 :Text;
            }

            struct Foo {
                key @0 :Person;
            }
        """
        mod = self.compile(schema)
        buf = ('garbage0'
               '\x05\x00\x00\x00\x32\x00\x00\x00'  # ptr to name
               'garbage1'
               'dummy\x00\x00\x00')
        p = mod.Person.from_buffer(buf, 8, 0, 1)
        foo = mod.Foo(p)
        assert foo.key.name == 'dummy'
        # we check that the structure has been packed
        assert foo.key._data_offset == 8
        assert foo.key._seg.buf[8:] == ('\x01\x00\x00\x00\x32\x00\x00\x00'  # ptr to dummy
                                      'dummy\x00\x00\x00')

    def test_compact_struct_inside_list(self):
        schema = """
            @0xbf5147cbbecf40c1;
            struct Person {
                name @0 :Text;
                surname @1 :Text;
            }

            struct Town {
                people @0 :List(Person);
            }
        """
        mod = self.compile(schema)
        p1 = mod.Person('Mickey', 'Mouse')
        p2 = mod.Person('Donald', 'Duck')
        t = mod.Town([p1, p2])
        assert t.people[0].name == 'Mickey'
        assert t.people[0].surname == 'Mouse'
        assert t.people[1].name == 'Donald'
        assert t.people[1].surname == 'Duck'

    def test_dump_list_of_bool(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            items @0 :List(Bool);
        }
        """
        mod = self.compile(schema)
        buf = ('\x01\x00\x00\x00\x19\x00\x00\x00'    # ptrlist
               '\x03\x00\x00\x00\x00\x00\x00\x00')
        f1 = mod.Foo.from_buffer(buf, 0, 0, 1)
        f2 = mod.Foo.loads(f1.dumps())
        assert list(f1.items) == list(f2.items) == [True, True, False]
