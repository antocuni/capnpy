import py
from capnpy.testing.compiler.support import CompilerTest
from capnpy.message import loads, dumps

class TestEvolution(CompilerTest):

    def test_add_data_field(self):
        schema = """
            @0xbf5147cbbecf40c1;
            struct Old {
                x @0 :Int64;
                y @1 :Int64;
            }

            struct New {
                x @0 :Int64;
                y @1 :Int64;
                z @2 :Int64 = 42;
            }
        """
        mod = self.compile(schema)
        # 1. read an old object with a newer schema
        s = dumps(mod.Old(x=1, y=2))
        obj = loads(s, mod.New)
        assert obj.x == 1
        assert obj.y == 2
        assert obj.z == 42
        #
        # 2. read a new object with an older schema
        s = dumps(mod.New(x=1, y=2, z=3))
        obj = loads(s, mod.Old)
        assert obj.x == 1
        assert obj.y == 2
        assert obj._data_size == 3
        py.test.raises(AttributeError, "obj.z")

    def test_add_ptr_field(self):
        schema = """
            @0xbf5147cbbecf40c1;
            struct Point {
                x @0 :Int64;
                y @1 :Int64;
            }

            struct Old {
                p1 @0 :Point;
            }

            struct New {
                p1 @0 :Point;
                p2 @1 :Point;
            }
        """
        mod = self.compile(schema)
        # 1. read an old object with a newer schema
        s = dumps(mod.Old(p1=mod.Point(x=1, y=2)))
        obj = loads(s, mod.New)
        assert obj.p1.x == 1
        assert obj.p1.y == 2
        assert obj.p2 is None
        # 2. read a new object with an older schema
        s = dumps(mod.New(p1=mod.Point(x=1, y=2),
                          p2=mod.Point(x=3, y=4)))
        obj = loads(s, mod.Old)
        assert obj.p1.x == 1
        assert obj.p1.y == 2
        assert obj._data_size == 0
        assert obj._ptrs_size == 2
        py.test.raises(AttributeError, "obj.p2")
