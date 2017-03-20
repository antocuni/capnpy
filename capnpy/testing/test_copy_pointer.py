from capnpy.copy_pointer import MutableBuffer

class TestMutableBuffer(object):

    def test_allocate(self):
        buf = MutableBuffer()
        buf.allocate(8)
        s = buf.as_bytes()
        assert s == '\x00' * 8
