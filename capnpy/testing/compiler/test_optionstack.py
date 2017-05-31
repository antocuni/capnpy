import pytest
from capnpy.compiler.options import OptionStack
from capnpy import annotate

class Options(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class TestOptionStack(object):

    def test_simple(self):
        a = Options(foo=1, bar=2)
        opt = OptionStack(a)
        assert opt.foo == 1
        assert opt.bar == 2
        pytest.raises(AttributeError, "opt.foobar")

    def test_shadow(self):
        a = Options(foo=1, bar=2)
        b = Options(foo=3, bar=4)
        opt = OptionStack()
        opt.push(a)
        opt.push(b)
        assert opt.foo == 3
        assert opt.bar == 4
        #
        opt.pop()
        assert opt.foo == 1
        assert opt.bar == 2

    def test_fall_through(self):
        a = Options(foo=1, bar=2)
        b = Options(foo=3, bar=None)
        opt = OptionStack()
        opt.push(a)
        opt.push(b)
        assert opt.foo == 3
        assert opt.bar == 2

    def test_notset(self):
        a = annotate.Options(convert_case=True)
        b = annotate.Options(convert_case=annotate.BoolOption.notset)
        opt = OptionStack()
        opt.push(a)
        opt.push(b)
        assert opt.convert_case == True
