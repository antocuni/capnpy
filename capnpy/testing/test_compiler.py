from capnpy.compiler import compile_file

def compile_string(tmpdir, s):
    tmp_capnp = tmpdir.join('tmp.capnp')
    tmp_capnp.write(s)
    return compile_file(tmp_capnp)


def test_simple_struct(tmpdir):
    schema = """
    @0xbf5147cbbecf40c1;
    struct Point {
        x @0 :Int64;
        y @1 :Int64;
    }
    """
    buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
           '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
    #
    mod = compile_string(tmpdir, schema)
    p = mod.Point.from_buffer(buf)
    assert p.x == 1
    assert p.y == 2

    
