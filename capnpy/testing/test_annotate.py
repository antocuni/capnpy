from capnpy.annotate import Options

def test_Options():
    opt = Options()
    assert opt.pyx is None
    assert opt.convert_case is None
    #
    opt = Options(pyx=True, convert_case=True)
    assert opt.pyx
    assert opt.convert_case
