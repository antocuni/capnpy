import py
from capnpy.enum import enum
from capnpy.struct_ import Struct

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
    py.test.raises(AttributeError, "Color.red.x = 42")

def test_read_enum():
    Color = enum('Color', ('red', 'green', 'blue', 'yellow'))
    Gender = enum('Gender', ('male', 'female', 'unknown'))
    #      color      gender     padding
    buf = '\x02\x00' '\x01\x00' '\x00\x00\x00\x00'
    
    blob = Struct.from_buffer(buf, 0, data_size=1, ptrs_size=0)
    color = blob._read_enum(0, Color)
    gender = blob._read_enum(2, Gender)
    assert color == Color.blue
    assert gender == Gender.female


def test_unknown():
    Color = enum('Color', ('red', 'green', 'blue'))
    assert type(Color) is type
    pink = Color(3)
    assert pink == 3
    assert pink.name == 'unknown<3>'

