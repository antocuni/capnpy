import py
import pytest
import struct

class TestUnpack(object):

    N = 2000

    @pytest.mark.benchmark(group="unpack")
    def test_unpack_primitive_int64(self, benchmark):
        from capnpy.unpack import unpack_primitive
        #
        def sum_unpack(buf):
            mybufs = (buf, buf)
            res = 0
            for i in range(self.N):
                buf = mybufs[i%2]
                res += unpack_primitive(ord('q'), buf, 16)
            return res
        #
        buf = struct.pack('qqq', 1000, 2000, 42)
        res = benchmark(sum_unpack, buf)
        assert res == self.N*42

    @pytest.mark.benchmark(group="unpack")
    def test_unpack_int64(self, benchmark):
        from capnpy.unpack import unpack_int64
        #
        def sum_unpack(buf):
            mybufs = (buf, buf)
            res = 0
            for i in range(self.N):
                buf = mybufs[i%2]
                res += unpack_int64(buf, 16)
            return res
        #
        buf = struct.pack('qqq', 1000, 2000, 42)
        res = benchmark(sum_unpack, buf)
        assert res == self.N*42
