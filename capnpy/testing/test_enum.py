import py
from capnpy.enum import enum

def test_enum():
    Color = enum('Color', ('red', 'green', 'blue'))
    assert type(Color) is type
    assert Color.red == 0
    assert Color.green == 1
    assert Color.blue == 2
    assert Color.red.name == 'red'
    assert repr(Color.red) == '<Color.red: 0>'
    assert str(Color.red) == 'Color.red'
    assert Color(0) == Color.red
    py.test.raises(ValueError, "Color(3)")
    py.test.raises(ValueError, "Color(-1)")
