import textwrap
from capnpy.__main__ import main

def test_compile(tmpdir):
    schema = textwrap.dedent("""
    @0xbf5147cbbecf40c1;
    struct Point {
        x @0 :Int64;
        y @1 :Int64;
    }
    """)
    example_capnp = tmpdir.join('example.capnp')
    example_capnp.write(schema)
    argv = ['compile', str(example_capnp), '--no-pyx']
    main(argv)
    assert tmpdir.join('example.py').exists()

