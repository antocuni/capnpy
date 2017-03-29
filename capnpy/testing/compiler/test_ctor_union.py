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
            fooBar @5 :Void;
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
        assert s._seg.buf == buf
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
        assert s._seg.buf == buf

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
        p = mod.Shape.new_empty(1, 2, color='red')
        assert p.area == 1
        assert p.perimeter == 2
        assert p.color == 'red'
        #
        p = mod.Shape.new_square(1, 2, 3, color='red')
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
        s = mod.Shape(area=1, perimeter=2)
        assert s.is_circle()
        assert s.area == 1
        assert s.perimeter == 2

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

    def test_generic(self):
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
        mod = self.compile(schema)
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

    def test_many_unions_arbitrary_order(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Person {
          name @0 :Text;
          union {
              male @1 :Void;
              female @4 :Void;
          }
          location :union {
              home @2 :Void;
              work @7 :Void;
          }
          job :union {
              unemployed @3 :Void;
              retired @5 :Void;
              worker @6 :Text;
          }
        }
        """
        mod = self.compile(schema)
        p = mod.Person.new_male(name='foo',
                                location=mod.Person.Location(work=None),
                                job=mod.Person.Job(worker='capnpy'))
        assert p.is_male()
        assert p.location.is_work()
        assert p.job.is_worker()
        assert p.job.worker == 'capnpy'

    def test_nested_unions(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Person {
          name @0 :Text;
          job :union {
              unemployed @1 :Void;
              retired @2 :Void;
              employed :group {
                  companyName @3 :Text;
                  union {
                      finance @4 :Void;
                      it @5 :Void;
                      other @6 :Void;
                  }
                  position :union {
                      manager @7 :Void;
                      worker @8 :Void;
                  }
              }
          }
        }
        """
        mod = self.compile(schema)
        p = mod.Person(
            name='foo',
            job=mod.Person.Job(
                employed=mod.Person_job.Employed(
                    company_name='capnpy',
                    it=None,
                    position=mod.Person_job_employed.Position(worker=None)
                )
            )
        )
        assert p.name == 'foo'
        assert p.job.is_employed()
        assert p.job.employed.company_name == 'capnpy'
        assert p.job.employed.is_it()
        assert p.job.employed.position.is_worker()

    def test_dont_overwrite_tags(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            union {
                a :union {
                    f0 @0 :Void;
                    f1 @1 :Void;
                }
                b :union {
                    f2 @2 :Void;
                    f3 @3 :Void;
                }
            }
        }
        """
        mod = self.compile(schema)
        foo = mod.Foo(a=mod.Foo.A(f1=None))
        assert foo.is_a()
        assert foo.a.is_f1()
