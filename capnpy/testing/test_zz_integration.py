"""
Integration tests which don't fit anywhere else :)
"""

from capnpy.testing.test_compiler import compile_string

def test_listbuilder_bug(tmpdir):
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
    mod = compile_string(tmpdir, schema)
    bars = [mod.Bar(1, 2)]
    foo = mod.Foo('name', bars)
    assert len(foo.bars) == 1
    assert foo.bars[0].x == 1
    assert foo.bars[0].y == 2


def test_listbuilder_null_ptrs(tmpdir):
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
    mod = compile_string(tmpdir, schema)
    a = mod.Bar(1, 2, None)
    b = mod.Bar(3, 4, None)
    foo = mod.Foo([a, b])
    a1 = foo.bars[0]
    assert a1.x == 1
    assert a1.y == 2
    assert a1.name is None
