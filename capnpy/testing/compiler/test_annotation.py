from capnpy.testing.compiler.support import CompilerTest

class TestAnnotation(CompilerTest):

    def test_simple(self):
        schema = """
        @0xbf5147cbbecf40c1;
        annotation foo @0xf8a1bedf44c89f00 (struct, group) :Void;
        """
        mod = self.compile(schema)
        assert mod.foo.__id__ == 0xf8a1bedf44c89f00
        assert not mod.foo.targets_file
        assert mod.foo.targets_struct
        assert mod.foo.targets_group
