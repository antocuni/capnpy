from capnpy import schema

def test_new_Type():
    t = schema.Type.new_int16()
    assert t.which() == t.__tag__.int16
    assert t.is_primitive()
    #
    t = schema.Type.new_void()
    assert t.which() == t.__tag__.void
    assert t.is_void()

def test_new_Field():
    t = schema.Type.new_int16()
    f = schema.Field.new_slot('field_name', offset=8, type=t)
    assert f.name == 'field_name'
    assert f.is_slot()
    assert f.slot.type.which() == schema.Type.__tag__.int16
    assert f.slot.offset == 8

    
