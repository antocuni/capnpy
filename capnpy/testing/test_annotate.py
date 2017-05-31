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
