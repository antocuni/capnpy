import py
import pytest
from capnpy.testing.compiler.support import CompilerTest

class BaseTestUnionConstructors(CompilerTest):

    @py.test.fixture
    def mod(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Shape {
          area @0 :Int64;
          perimeter @1 :Int64;
          union {
            circle @2 :Int64;      # radius
            square @3 :Int64;      # width
            empty  @4 :Void;
          }
        }
        """
        return self.compile(schema)


class TestSpecificCtors(BaseTestUnionConstructors):

    def test_simple(self, mod):
        s = mod.Shape.new_circle(area=1, circle=2, perimeter=3)
        assert s.which() == mod.Shape.__tag__.circle
        assert s.area == 1
        assert s.circle == 2
        assert s.perimeter == 3
        buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'   # area == 1
               '\x03\x00\x00\x00\x00\x00\x00\x00'   # perimeter == 3
               '\x02\x00\x00\x00\x00\x00\x00\x00'   # circle == 2
               '\x00\x00\x00\x00\x00\x00\x00\x00')  # __tag__ == 0 (circle)
        assert s._buf.s == buf
        #
        s = mod.Shape.new_square(area=1, square=2, perimeter=3)
        assert s.which() == mod.Shape.__tag__.square
        assert s.area == 1
        assert s.square == 2
        assert s.perimeter == 3
        buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'   # area == 1
               '\x03\x00\x00\x00\x00\x00\x00\x00'   # perimeter == 3
               '\x02\x00\x00\x00\x00\x00\x00\x00'   # squadre == 2
               '\x01\x00\x00\x00\x00\x00\x00\x00')  # __tag__ == 1 (square)
        assert s._buf.s == buf

    def test_default(self, mod):
        p = mod.Shape.new_circle()
        assert p.circle == 0
        assert p.area == 0
        assert p.perimeter == 0
        assert p.is_circle()
        #
        p = mod.Shape.new_square()
        assert p.square == 0
        assert p.area == 0
        assert p.perimeter == 0
        assert p.is_square()
        #
        p = mod.Shape.new_empty()
        assert p.empty is None
        assert p.area == 0
        assert p.perimeter == 0
        assert p.is_empty()

    def test_no_void_args(self, mod):
        py.test.raises(TypeError, "mod.Shape.new_empty(empty=None)")
        p = mod.Shape.new_empty(1, 2)
        assert p.is_empty()
        assert p.empty is None
        assert p.area == 1
        assert p.perimeter == 2

    def test_args_order(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Shape {
          area @0 :Int64;
          perimeter @1 :Int64;
          union {
            circle @2 :Int64;      # radius
            square @3 :Int64;      # width
            empty  @4 :Void;
          }
          color @5 :Text;
        }
        """
        mod = self.compile(schema)
        # the order is: area, perimeter, [circle/square], color
        p = mod.Shape.new_empty(1, 2, 'red')
        assert p.area == 1
        assert p.perimeter == 2
        assert p.color == 'red'
        #
        p = mod.Shape.new_square(1, 2, 3, 'red')
        assert p.area == 1
        assert p.perimeter == 2
        assert p.square == 3
        assert p.color == 'red'


class TestGenericCtor(BaseTestUnionConstructors):

    def test_simple(self, mod):
        # test the __init__
        s = mod.Shape(area=1, square=2, perimeter=3)
        assert s.which() == mod.Shape.__tag__.square
        assert s.area == 1
        assert s.square == 2
        assert s.perimeter == 3

    def test_void_arg(self, mod):
        s = mod.Shape(area=1, empty=None, perimeter=3)
        assert s.which() == mod.Shape.__tag__.empty
        assert s.area == 1
        assert s.empty is None
        assert s.perimeter == 3

    def test_multiple_tags(self, mod):
        einfo = py.test.raises(TypeError,
                              "mod.Shape(area=0, perimeter=0, circle=1, square=2)")
        assert str(einfo.value) == ('got multiple values for the union tag: '
                                    'circle, square')

    def test_no_tags(self, mod):
        einfo = py.test.raises(TypeError, "mod.Shape(area=0, perimeter=0)")
        assert str(einfo.value) == ("one of the following args is required: "
                                    "circle, square, empty")


    def test_default(self, mod):
        p = mod.Shape(circle=42)
        assert p.area == 0
        assert p.perimeter == 0
        assert p.is_circle()
        assert p.circle == 42
        #
        p = mod.Shape(empty=None)
        assert p.area == 0
        assert p.perimeter == 0
        assert p.is_empty()


class TestNamedUnion(CompilerTest):

    @py.test.fixture
    def mod(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Person {
          name @0 :Text;
          job :union {
              unemployed @1 :Void;
              retired @2 :Void;
              worker @3 :Text;
          }
        }
        """
        return self.compile(schema)

    def test_generic(self, mod):
        p = mod.Person(name='foo', job=mod.Person.Job(unemployed=None))
        assert p.name == 'foo'
        assert p.job.is_unemployed()
        #
        p = mod.Person(name='foo', job=mod.Person.Job(retired=None))
        assert p.name == 'foo'
        assert p.job.is_retired()
        #
        p = mod.Person(name='foo', job=mod.Person.Job(worker='capnpy'))
        assert p.name == 'foo'
        assert p.job.worker == 'capnpy'
        #
        pytest.raises(TypeError, "mod.Person(name='foo', job=mod.Person.Job())")

    @pytest.mark.xfail
    def test_group_inside_union(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Person {
          name @0 :Text;
          job :union {
              unemployed @1 :Void;
              retired @2 :Void;
              worker @3 :Text;
              manager :group {
                  title @4 :Text;
                  company @5 :Text;
             }
          }
        }
        """
        mod = self.compile(schema)
        p = mod.Person(name='foo', job=mod.Person.Job(unemployed=None))
        assert p.job.is_unemployed()
