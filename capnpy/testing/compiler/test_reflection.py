import py
from six import b
from capnpy.reflection import get_reflection_data
from capnpy.testing.compiler.support import CompilerTest

class TestReflection(CompilerTest):

    def test___capnpy_id__(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
        }
        """
        mod = self.compile(schema)
        assert mod.__capnpy_id__ == 0xbf5147cbbecf40c1
        # we don't want to hardcode the exact value of Point's id, just check
        # that it exists
        assert mod.Point.__capnpy_id__

    def test_get_reflection_data(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
        }
        """
        mod = self.compile(schema)
        reflection = get_reflection_data(mod)
        reqfile = reflection.m.request.requestedFiles[0]
        assert reqfile.filename == b(mod.__file__)

    def test_get_node(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
        }
        """
        mod = self.compile(schema)
        reflection =  get_reflection_data(mod)
        mod_node = reflection.get_node(mod)
        assert mod_node.is_file()
        assert mod_node.id == 0xbf5147cbbecf40c1
        #
        point_node = reflection.get_node(mod.Point)
        assert point_node.is_struct
        assert point_node.shortname(reflection.m) == 'Point'

    def test_has_annotation(self):
        from capnpy import annotate
        schema = """
        @0xbf5147cbbecf40c1;
        using Py = import "/capnpy/annotate.capnp";
        struct Point $Py.key("x, y") {
            x @0 :Int64;
            y @1 :Int64;
        }
        """
        mod = self.compile(schema)
        reflection =  get_reflection_data(mod)
        node_Point = reflection.get_node(mod.Point)
        assert reflection.has_annotation(node_Point, annotate.key)
        assert reflection.has_annotation(mod.Point, annotate.key)
