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
