import pytest
from capnpy.copy_pointer import MutableBuffer

class TestMutableBuffer(object):

    def test_allocate(self):
        buf = MutableBuffer(16)
        buf.allocate(8)
        s = buf.as_bytes()
        assert s == '\x00' * 8

    def test_allocate_failure(self):
        buf = MutableBuffer(16)
        buf.allocate(8)
        buf.allocate(8)
        pytest.raises(ValueError, "buf.allocate(1)")
