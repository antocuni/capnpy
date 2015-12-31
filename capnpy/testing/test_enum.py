import py
from capnpy.enum import enum
from capnpy.blob import Blob

def test_enum():
    Color = enum('Color', ('red', 'green', 'blue'))
    assert type(Color) is type
    assert Color.red == 0
    assert Color.green == 1
    assert Color.blue == 2
    assert Color.red.name == 'red'
    assert repr(Color.red) == '<Color.red: 0>'
    assert str(Color.red) == 'red'
    assert Color(0) == Color.red
    py.test.raises(ValueError, "Color(3)")
    py.test.raises(ValueError, "Color(-1)")


def test_read_enum():
    Color = enum('Color', ('red', 'green', 'blue', 'yellow'))
    Gender = enum('Gender', ('male', 'female', 'unknown'))
    #      color      gender     padding
    buf = '\x02\x00' '\x01\x00' '\x00\x00\x00\x00'
    
    blob = Blob(buf, 0, None)
    color = blob._read_enum(0, Color)
    gender = blob._read_enum(2, Gender)
    assert color == Color.blue
    assert gender == Gender.female
    
