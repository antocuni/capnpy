import py
import pytest
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
        reqfile = reflection.m.request.requestedFiles[0].filename
        assert reqfile.endswith(b'tmp.capnp')

    def test_dont_include(self):
        schema = """
        @0xbf5147cbbecf40c1;
        using Py = import "/capnpy/annotate.capnp";
        $Py.options(includeReflectionData=false);

        struct Point {
            x @0 :Int64;
            y @1 :Int64;
        }
        """
        mod = self.compile(schema)
        assert not hasattr(mod, '_reflection_data')
        with pytest.raises(ValueError):
            get_reflection_data(mod)


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

    def test_allnodes(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Point {
            x @0 :Int64;
            y @1 :Int64;
        }
        """
        mod = self.compile(schema)
        reflection =  get_reflection_data(mod)
        assert mod.__capnpy_id__ in reflection.allnodes
        assert mod.Point.__capnpy_id__ in reflection.allnodes

    def test_get_annotation(self):
        from capnpy import annotate
        schema = """
        @0xbf5147cbbecf40c1;
        using Py = import "/capnpy/annotate.capnp";
        struct Point $Py.key("x, y") {
            x @0 :Int64;
            y @1 :Int64;
        }
        struct Foo {
        }
        """
        mod = self.compile(schema)
        reflection =  get_reflection_data(mod)
        node_Point = reflection.get_node(mod.Point)
        assert reflection.has_annotation(node_Point, annotate.key)
        assert reflection.has_annotation(mod.Point, annotate.key)
        assert not reflection.has_annotation(mod.Foo, annotate.key)
        #
        assert reflection.get_annotation(node_Point, annotate.key) == b'x, y'
        assert reflection.get_annotation(mod.Point, annotate.key) == b'x, y'
        #
        with pytest.raises(KeyError):
            reflection.get_annotation(mod.Foo, annotate.key)

    def test_get_annotation_fields(self):
        from capnpy import annotate
        schema = """
        @0xbf5147cbbecf40c1;
        annotation myAnnotation(field) :Text;
        struct Point {
            x @0 :Int64 $myAnnotation("hello");
            y @1 :Int64;
        }
        """
        mod = self.compile(schema)
        r =  get_reflection_data(mod)
        node_Point = r.get_node(mod.Point)
        fx, fy = node_Point.get_struct_fields()
        assert r.has_annotation(fx, mod.myAnnotation)
        assert r.get_annotation(fx, mod.myAnnotation) == b'hello'
        assert not r.has_annotation(fy, mod.myAnnotation)

    def test_get_annotation_enumerants(self):
        from capnpy import annotate
        schema = """
        @0xbf5147cbbecf40c1;
        annotation myAnnotation(enumerant) :Text;
        enum Color {
            red @0 $myAnnotation("hello");
            green @1;
        }
        """
        mod = self.compile(schema)
        r =  get_reflection_data(mod)
        node_Color = r.get_node(mod.Color)
        red, green = node_Color.get_enum_enumerants()
        assert r.has_annotation(red, mod.myAnnotation)
        assert r.get_annotation(red, mod.myAnnotation) == b'hello'
        assert not r.has_annotation(green, mod.myAnnotation)

    def test_options(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            myField @0 :Int64;
        }
        """
        mod = self.compile(schema, convert_case=False)
        reflection = get_reflection_data(mod)
        node = reflection.get_node(mod.Foo)
        assert node.is_struct
        assert node.shortname(reflection.m) == 'Foo'
        f = node.get_struct_fields()[0]
        fname = reflection.field_name(f)
        assert fname == 'myField'

    def test_enum(self):
        schema = """
        @0xbf5147cbbecf40c1;
        enum Color {
            lightRed @0;
            darkGreen @1;
        }
        """
        mod = self.compile(schema)
        reflection = get_reflection_data(mod)
        node = reflection.get_node(mod.Color)
        assert node.is_enum()
        enumerants = node.get_enum_enumerants()
        assert reflection.field_name(enumerants[0]) == 'light_red'
        assert reflection.field_name(enumerants[1]) == 'dark_green'
