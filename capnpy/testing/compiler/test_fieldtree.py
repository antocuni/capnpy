import py
import pytest
import textwrap
from capnpy.compiler.fieldtree import FieldTree
from capnpy.testing.compiler.support import CompilerTest

class TestFieldTree(CompilerTest):

    schema = """
    @0xbf5147cbbecf40c1;
    struct Person {
        name :group {
            first @0 :Text;
            last @1 :Text;
        }
        address :group {
            street @2 :Text;
            position :group {
                x @3 :Int64 = 42;
                y @4 :Int64;
            }
        }
    }
    """

    def find_struct(self, m, name):
        for node in m.allnodes.values():
            if node.is_struct() and node.shortname(m) == name:
                return node
        raise KeyError("Cannot find node %s" % name)

    def test_pprint(self, capsys):
        m = self.getm(self.schema)
        person = self.find_struct(m, 'Person')
        tree = FieldTree(m, person.struct)
        tree.pprint()
        out, err = capsys.readouterr()
        out = out.strip()
        assert out == textwrap.dedent("""
        <FieldTree>
            <Node name: group>
                <Node name_first: slot>
                <Node name_last: slot>
            <Node address: group>
                <Node address_street: slot>
                <Node address_position: group>
                    <Node address_position_x: slot>
                    <Node address_position_y: slot>
        """).strip()

    def test_allnodes(self):
        m = self.getm(self.schema)
        person = self.find_struct(m, 'Person')
        tree = FieldTree(m, person.struct)
        nodes = tree.allnodes()
        varnames = [node.varname for node in nodes]
        assert varnames == ['name',
                            'name_first',
                            'name_last',
                            'address',
                            'address_street',
                            'address_position',
                            'address_position_x',
                            'address_position_y']

    def test_default(self):
        m = self.getm(self.schema)
        person = self.find_struct(m, 'Person')
        tree = FieldTree(m, person.struct)
        items = [(node.varname, node.default) for node in tree.allnodes()]
        assert items == [
            ('name', '(None, None,)'),
            ('name_first', 'None'),
            ('name_last', 'None'),
            ('address', '(None, (42, 0,),)'),
            ('address_street', 'None'),
            ('address_position', '(42, 0,)'),
            ('address_position_x', '42'),
            ('address_position_y', '0'),
        ]

    def test_args_and_params(self):
        m = self.getm(self.schema)
        person = self.find_struct(m, 'Person')
        tree = FieldTree(m, person.struct)
        args, params = tree.get_args_and_params()
        assert args == ['name', 'address']
        params = [(varname, eval(default)) for varname, default in params]
        assert params == [
            ('name', (None, None)),
            ('address', (None, (42, 0)))
            ]

    def test_args_and_params_union(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Baz {
            union {
                foo @0 :Int64;
                bar @1 :Int64;
            }
        }
        """
        m = self.getm(schema)
        baz = self.find_struct(m, 'Baz')
        tree = FieldTree(m, baz.struct)
        args, params = tree.get_args_and_params()
        assert params == [
            ('foo', '_undefined'),
            ('bar', '_undefined'),
            ]
        #
        f_bar = baz.struct.fields[1]
        tree = FieldTree(m, baz.struct, field_force_default=f_bar)
        args, params = tree.get_args_and_params()
        assert params == [
            ('foo', '_undefined'),
            ('bar', '0'),
            ]

    def test_void_args(self):
        schema = """
        @0xbf5147cbbecf40c1;
        struct Foo {
            a @0 :Int64;
            b @1 :Void;
            bar :group {
                c @2 :Int64;
                d @3 :Void;
            }
            baz :union {
                e @4 :Int64;
                f @5 :Void;
            }
        }
        """
        m = self.getm(schema)
        foo = self.find_struct(m, 'Foo')
        tree = FieldTree(m, foo.struct)
        varnames = [node.varname for node in tree.allnodes()]
        assert varnames == ['a', 'bar', 'bar_c', 'baz', 'baz_e', 'baz_f']
