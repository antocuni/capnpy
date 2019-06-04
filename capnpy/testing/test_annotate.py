import pytest
from capnpy.annotate import Options, BoolOption, TextType

class TestOptions:

    def test_simple(self):
        opt = Options()
        assert opt.convert_case == BoolOption.notset
        #
        opt = Options(convert_case=True)
        assert opt.convert_case == True
        #
        opt = Options(convert_case=False)
        assert opt.convert_case == False

    def test_BoolOption(self):
        assert BoolOption.true
        assert not BoolOption.false
        pytest.raises(ValueError, "bool(BoolOption.notset)")
        #
        t = BoolOption(True)
        assert t == BoolOption.true
        #
        f = BoolOption(False)
        assert f == BoolOption.false

    def test_FIELDS(self):
        # make sure that we listed all the FIELDS
        all_props = [name for name in dir(Options)
                     if isinstance(getattr(Options, name), property)]
        all_props.sort()
        assert all_props == sorted(Options.FIELDS)

    def test_combine_bool(self):
        t = Options(convert_case=True)
        f = Options(convert_case=False)
        n = Options()
        assert f.combine(t).convert_case == True
        assert f.combine(n).convert_case == False
        assert t.combine(f).convert_case == False
        assert t.combine(n).convert_case == True
        assert n.combine(t).convert_case == True
        assert n.combine(f).convert_case == False

    def test_combine_text_type(self):
        b = Options(text_type=TextType.bytes)
        u = Options(text_type=TextType.unicode)
        n = Options()
        assert b.combine(u).text_type == TextType.unicode
        assert b.combine(n).text_type == TextType.bytes
        assert u.combine(b).text_type == TextType.bytes
        assert u.combine(n).text_type == TextType.unicode
        assert n.combine(b).text_type == TextType.bytes
        assert n.combine(u).text_type == TextType.unicode
