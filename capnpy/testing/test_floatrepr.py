import pytest
pytest.importorskip("capnpy.floatrepr")
from capnpy.floatrepr import float32_repr, float64_repr
    
def test_float32_repr():
    x = 193.161239624
    assert repr(x) == '193.161239624'
    assert float32_repr(x) == '193.16124'


def test_float64_repr():
    x = 1449058511.746721
    assert float64_repr(x) == '1449058511.746721'
