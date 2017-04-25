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

def test_unknown():
    Color = enum('Color', ('red', 'green', 'blue'))
    assert type(Color) is type
    pink = Color(3)
    assert pink == 3
    assert pink.name == 'unknown<3>'
