import pytest
from capnpy.annotate import Options, BoolOption

def test_Options():
    opt = Options()
    assert opt.convert_case == BoolOption.notset
    #
    opt = Options(convert_case=True)
    assert opt.convert_case == True
    #
    opt = Options(convert_case=False)
    assert opt.convert_case == False

def test_BoolOption():
    assert BoolOption.true
    assert not BoolOption.false
    pytest.raises(ValueError, "bool(BoolOption.notset)")
    #
    t = BoolOption(True)
    assert t == BoolOption.true
    #
    f = BoolOption(False)
    assert f == BoolOption.false

def test_FIELDS():
    # make sure that we listed all the FIELDS
    all_props = [name for name in dir(Options)
                 if isinstance(getattr(Options, name), property)]
    all_props.sort()
    assert all_props == sorted(Options.FIELDS)

def test_combine():
    t = Options(convert_case=True)
    f = Options(convert_case=False)
    u = Options()
    assert f.combine(t).convert_case == True
    assert f.combine(u).convert_case == False
    assert t.combine(f).convert_case == False
    assert t.combine(u).convert_case == True
    assert u.combine(t).convert_case == True
    assert u.combine(f).convert_case == False
