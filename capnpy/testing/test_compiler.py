from capnpy.compiler import compile_file

def compile_string(tmpdir, s):
    tmp_capnp = tmpdir.join('tmp.capnp')
    tmp_capnp.write(s)
    return compile_file(tmp_capnp)


def test_primitive(tmpdir):
    schema = """
    @0xbf5147cbbecf40c1;
    struct Point {
        x @0 :Int64;
        y @1 :Int64;
    }
    """
    mod = compile_string(tmpdir, schema)
    #
    buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
           '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
    p = mod.Point.from_buffer(buf)
    assert p.x == 1
    assert p.y == 2


def test_string(tmpdir):
    schema = """
    @0xbf5147cbbecf40c1;
    struct Foo {
        x @0 :Int64;
        name @1 :Text;
    }
    """
    mod = compile_string(tmpdir, schema)

    buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'   # 1
           '\x01\x00\x00\x00\x82\x00\x00\x00'   # ptrlist
           'hello capnproto\0')                 # string

    f = mod.Foo.from_buffer(buf)
    assert f.x == 1
    assert f.name == 'hello capnproto'


def test_list(tmpdir):
    schema = """
    @0xbf5147cbbecf40c1;
    struct Foo {
        items @0 :List(Int64);
    }
    """
    mod = compile_string(tmpdir, schema)
    
    buf = ('\x01\x00\x00\x00\x25\x00\x00\x00'   # ptrlist
           '\x01\x00\x00\x00\x00\x00\x00\x00'   # 1
           '\x02\x00\x00\x00\x00\x00\x00\x00'   # 2
           '\x03\x00\x00\x00\x00\x00\x00\x00'   # 3
           '\x04\x00\x00\x00\x00\x00\x00\x00')  # 4
    f = mod.Foo.from_buffer(buf, 0)
    assert f.items == [1, 2, 3, 4]


def test_struct(tmpdir):
    schema = """
    @0xbf5147cbbecf40c1;
    struct Point {
        x @0 :Int64;
        y @1 :Int64;
    }
    struct Rectangle {
        a @0 :Point;
        b @1 :Point;
    }
    """
    mod = compile_string(tmpdir, schema)
    buf = ('\x04\x00\x00\x00\x02\x00\x00\x00'    # ptr to a
           '\x08\x00\x00\x00\x02\x00\x00\x00'    # ptr to b
           '\x01\x00\x00\x00\x00\x00\x00\x00'    # a.x == 1
           '\x02\x00\x00\x00\x00\x00\x00\x00'    # a.y == 2
           '\x03\x00\x00\x00\x00\x00\x00\x00'    # b.x == 3
           '\x04\x00\x00\x00\x00\x00\x00\x00')   # b.y == 4

    r = mod.Rectangle.from_buffer(buf)
    assert r.a.x == 1
    assert r.a.y == 2
    assert r.b.x == 3
    assert r.b.y == 4

def test_enum(tmpdir):
    schema = """
    @0xbf5147cbbecf40c1;
    enum Color {
        red @0;
        green @1;
        blue @2;
        yellow @3;
    }
    enum Gender {
        male @0;
        female @1;
        unknown @2;
    }
    struct Foo {
        color @0 :Color;
        gender @1 :Gender;
    }
    """
    mod = compile_string(tmpdir, schema)
    buf = '\x02\x00' '\x01\x00' '\x00\x00\x00\x00'
    f = mod.Foo.from_buffer(buf)
    assert f.color == mod.Color.blue
    assert f.gender == mod.Gender.female
