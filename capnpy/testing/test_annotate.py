from capnpy.annotate import Options

def test_Options():
    opt = Options()
    assert opt.convert_case is None
    #
    opt = Options(convert_case=True)
    assert opt.convert_case
