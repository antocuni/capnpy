from capnpy.util import extend

def test_extend():
    class Foo(object):
        pass

    @extend(Foo)
    class Bar(object):
        a = 42
        def foo(self):
            return 123

    assert Bar is Foo
    assert Foo.a == 42
    assert Foo().foo() == 123
