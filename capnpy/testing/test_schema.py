from capnpy import schema

def test_new_Type():
    t = schema.Type.new_int16()
    assert t.which() == t.__tag__.int16
    assert t.is_primitive()
    #
    t = schema.Type.new_void()
    assert t.which() == t.__tag__.void
    assert t.is_void()
    
