import py
import capnpy
from capnpy.compiler import Compiler

def compile_string(tmpdir, s):
    # root is needed to be able to import capnpy/py.capnp
    root = py.path.local(capnpy.__file__).dirpath('..')
    comp = Compiler([root, tmpdir])
    tmp_capnp = tmpdir.join('tmp.capnp')
    tmp_capnp.write(s)
    return comp.load_schema('/tmp.capnp')


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
    p = mod.Point.from_buffer(buf, 0, None)
    assert p.x == 1
    assert p.y == 2

def test_primitive_default(tmpdir):
    schema = """
    @0xbf5147cbbecf40c1;
    struct Foo {
        x @0 :Int64 = 42;
        y @1 :Bool = true;
    }
    """
    mod = compile_string(tmpdir, schema)
    #
    buf = ('\x00\x00\x00\x00\x00\x00\x00\x00'
           '\x00\x00\x00\x00\x00\x00\x00\x00')
    p = mod.Foo.from_buffer(buf, 0, None)
    assert p.x == 42
    assert p.y is True


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

    f = mod.Foo.from_buffer(buf, 0, None)
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
    f = mod.Foo.from_buffer(buf, 0, None)
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

    r = mod.Rectangle.from_buffer(buf, 0, None)
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
    f = mod.Foo.from_buffer(buf, 0, None)
    assert f.color == mod.Color.blue
    assert f.gender == mod.Gender.female


def test_union(tmpdir):
    schema = """
    @0xbf5147cbbecf40c1;
    struct Shape {
      area @0 :Int64;
      union {
        circle @1 :Int64;      # radius
        square @2 :Int64;      # width
      }
    }
    """
    mod = compile_string(tmpdir, schema)
    buf = ('\x40\x00\x00\x00\x00\x00\x00\x00'     # area == 64
           '\x08\x00\x00\x00\x00\x00\x00\x00'     # square == 8
           '\x01\x00\x00\x00\x00\x00\x00\x00')    # which() == square, padding
    shape = mod.Shape.from_buffer(buf, 0, None)
    assert shape.area == 64
    assert shape.which() == mod.Shape.__tag__.square
    assert shape.square == 8
    py.test.raises(ValueError, "shape.circle")


def test_group(tmpdir):
    schema = """
    @0xbf5147cbbecf40c1;
    struct Rectangle {
        a :group {
            x @0 :Int64;
            y @1 :Int64;
        }
        b :group {
            x @2 :Int64;
            y @3 :Int64;
        }
    }
    """
    mod = compile_string(tmpdir, schema)
    buf = ('garbage0'
           '\x01\x00\x00\x00\x00\x00\x00\x00'    # a.x == 1
           '\x02\x00\x00\x00\x00\x00\x00\x00'    # a.y == 2
           '\x03\x00\x00\x00\x00\x00\x00\x00'    # b.x == 3
           '\x04\x00\x00\x00\x00\x00\x00\x00')   # b.y == 4
    r = mod.Rectangle.from_buffer(buf, 8)
    assert r.a.x == 1
    assert r.a.y == 2
    assert r.b.x == 3
    assert r.b.y == 4

def test_group(tmpdir):
    schema = """
    @0xbf5147cbbecf40c1;
    struct Shape {
      union {
        circle :group {
          radius @0 :Int64;
        }
        rectangle :group {
          width @1 :Int64;
          height @2 :Int64;
        }
      }
    }
    """
    mod = compile_string(tmpdir, schema)
    buf = ('\x04\x00\x00\x00\x00\x00\x00\x00'    # rectangle.width == 4
           '\x01\x00\x00\x00\x00\x00\x00\x00'    # which() == rectangle, padding
           '\x05\x00\x00\x00\x00\x00\x00\x00')   # rectangle.height == 5

    shape = mod.Shape.from_buffer(buf, 0, None)
    assert shape.which() == mod.Shape.__tag__.rectangle
    assert shape.rectangle.width == 4
    assert shape.rectangle.height == 5


def test_nested_struct(tmpdir):
    schema = """
    @0xbf5147cbbecf40c1;
    struct Outer {
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
        }
    }
    """
    mod = compile_string(tmpdir, schema)
    #
    buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
           '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
    p = mod.Outer.Point.from_buffer(buf, 0, None)
    assert p.x == 1
    assert p.y == 2


def test_const(tmpdir):
    schema = """
    @0xbf5147cbbecf40c1;
    struct Foo {
        const bar :UInt16 = 42;
    }
    """
    mod = compile_string(tmpdir, schema)
    assert mod.Foo.bar == 42


def test_list_of_structs(tmpdir):
    schema = """
    @0xbf5147cbbecf40c1;
    struct Polygon {
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
        }
        points @0 :List(Point);
    }
    """
    mod = compile_string(tmpdir, schema)
    buf = ('\x01\x00\x00\x00\x47\x00\x00\x00'    # ptrlist
           '\x10\x00\x00\x00\x02\x00\x00\x00'    # list tag
           '\x0a\x00\x00\x00\x00\x00\x00\x00'    # 10
           '\x64\x00\x00\x00\x00\x00\x00\x00'    # 100
           '\x14\x00\x00\x00\x00\x00\x00\x00'    # 20
           '\xc8\x00\x00\x00\x00\x00\x00\x00'    # 200
           '\x1e\x00\x00\x00\x00\x00\x00\x00'    # 30
           '\x2c\x01\x00\x00\x00\x00\x00\x00'    # 300
           '\x28\x00\x00\x00\x00\x00\x00\x00'    # 40
           '\x90\x01\x00\x00\x00\x00\x00\x00')   # 400
    poly = mod.Polygon.from_buffer(buf, 0, None)
    assert len(poly.points) == 4
    assert poly.points[0].x == 10
    assert poly.points[0].y == 100

def test_bool(tmpdir):
    schema = """
    @0xbf5147cbbecf40c1;
    struct Foo {
        padding @0 :Int64;
        a @1 :Bool;
        b @2 :Bool;
        c @3 :Bool;
    }
    """
    mod = compile_string(tmpdir, schema)
    buf = ('\x00\x00\x00\x00\x00\x00\x00\x00'   # padding
           '\x05\x00\x00\x00\x00\x00\x00\x00')  # True, False, True, padding
    p = mod.Foo.from_buffer(buf, 0, None)
    assert p.a == True
    assert p.b == False
    assert p.c == True



def test_ctor_simple(tmpdir):
    schema = """
    @0xbf5147cbbecf40c1;
    struct Point {
        x @0 :Int64;
        y @1 :Int64;
    }
    """
    mod = compile_string(tmpdir, schema)
    buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
           '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
    #
    p = mod.Point(1, 2)
    assert p.x == 1
    assert p.y == 2
    assert p._buf == buf

def test_ctor_string(tmpdir):
    schema = """
    @0xbf5147cbbecf40c1;
    struct Foo {
        x @0 :Int64;
        y @1 :Text;
    }
    """
    mod = compile_string(tmpdir, schema)
    foo = mod.Foo(1, 'hello capnp')
    assert foo._buf == ('\x01\x00\x00\x00\x00\x00\x00\x00'
                        '\x01\x00\x00\x00\x62\x00\x00\x00'
                        'h' 'e' 'l' 'l' 'o' ' ' 'c' 'a'
                        'p' 'n' 'p' '\x00\x00\x00\x00\x00')



class TestUnionConstructors(object):

    @py.test.fixture
    def mod(self, tmpdir):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Shape {
          area @0 :Int64;
          perimeter @1 :Int64;
          union {
            circle @2 :Int64;      # radius
            square @3 :Int64;      # width
          }
        }
        """
        return compile_string(tmpdir, schema)

    def test_specific_ctors(self, mod):
        s = mod.Shape.new_circle(area=1, circle=2, perimeter=3)
        assert s.which() == mod.Shape.__tag__.circle
        assert s.area == 1
        assert s.circle == 2
        assert s.perimeter == 3
        #
        s = mod.Shape.new_square(area=1, square=2, perimeter=3)
        assert s.which() == mod.Shape.__tag__.square
        assert s.area == 1
        assert s.square == 2
        assert s.perimeter == 3

    def test_generic_ctor(self, mod):
        # test the __new__
        s = mod.Shape(area=1, square=2, perimeter=3)
        assert s.which() == mod.Shape.__tag__.square
        assert s.area == 1
        assert s.square == 2
        assert s.perimeter == 3
    
    def test_multiple_tags(self, mod):
        einfo = py.test.raises(TypeError,
                              "mod.Shape(area=0, perimeter=0, circle=1, square=2)")
        assert str(einfo.value) == 'got multiple values for the union tag: square, circle'

    def test_no_tags(self, mod):
        einfo = py.test.raises(TypeError, "mod.Shape(area=0, perimeter=0)")
        assert str(einfo.value) == "one of the following args is required: circle, square"


def test_convert_case_fields(tmpdir):
    schema = """
    @0xbf5147cbbecf40c1;
    struct MyStruct {
        firstAttr @0 :Int64;
        secondAttr @1 :Int64;
    }
    """
    mod = compile_string(tmpdir, schema)
    assert mod.MyStruct.first_attr.name == 'first_attr'
    assert mod.MyStruct.second_attr.name == 'second_attr'

def test_convert_case_enum(tmpdir):
    schema = """
    @0xbf5147cbbecf40c1;
    enum Foo {
        firstItem @0;
        secondItem @1;
    }
    """
    mod = compile_string(tmpdir, schema)
    assert mod.Foo.first_item == 0
    assert mod.Foo.second_item == 1


def test_name_clash(tmpdir):
    schema = """
    @0xbf5147cbbecf40c1;
    struct Types {
    }
    struct Point {
        x @0 :Int64;
        y @1 :Int64;
    }
    """
    mod = compile_string(tmpdir, schema)
    #
    buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
           '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
    p = mod.Point.from_buffer(buf, 0, None)
    assert p.x == 1
    assert p.y == 2


def test_dont_load_twice(tmpdir):
    schema = """
    @0xbf5147cbbecf40c1;
    struct Point {
        x @0 :Int64;
        y @1 :Int64;
    }
    """
    tmpdir.join("tmp.capnp").write(schema)
    comp = Compiler([tmpdir])
    mod1 = comp.load_schema("/tmp.capnp")
    mod2 = comp.load_schema("/tmp.capnp")
    assert mod1 is mod2
    

def test_import(tmpdir):
    comp = Compiler([tmpdir])
    tmpdir.join("p.capnp").write("""
    @0xbf5147cbbecf40c1;
    struct Point {
        x @0 :Int64;
        y @1 :Int64;
    }
    """)
    tmpdir.join("tmp.capnp").write("""
    @0xbf5147cbbecf40c2;
    using P = import "/p.capnp";
        struct Rectangle {
        a @0 :P.Point;
        b @1 :P.Point;
    }
    """)
    mod = comp.load_schema("/tmp.capnp")

def test_import_absolute(tmpdir):
    one = tmpdir.join('one').ensure(dir=True)
    two = tmpdir.join('two').ensure(dir=True)
    
    comp = Compiler([tmpdir])
    one.join("p.capnp").write("""
    @0xbf5147cbbecf40c1;
    struct Point {
        x @0 :Int64;
        y @1 :Int64;
    }
    """)
    two.join("tmp.capnp").write("""
    @0xbf5147cbbecf40c2;
    using P = import "/one/p.capnp";
        struct Rectangle {
        a @0 :P.Point;
        b @1 :P.Point;
    }
    """)
    mod = comp.load_schema("/two/tmp.capnp")

def test_nullable(tmpdir):
    schema = """
    @0xbf5147cbbecf40c1;
    using Py = import "/capnpy/py.capnp";
    struct Foo {
        x :group $Py.nullable {
            isNull @0 :Int8;
            value  @1 :Int64;
        }
    }
    """
    mod = compile_string(tmpdir, schema)
    buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
           '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
    foo = mod.Foo.from_buffer(buf, 0, None)
    assert foo._x_is_null
    assert foo.x is None
    #
    buf = ('\x00\x00\x00\x00\x00\x00\x00\x00'  # 0
           '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
    foo = mod.Foo.from_buffer(buf, 0, None)
    assert not foo._x_is_null
    assert foo.x == 2
