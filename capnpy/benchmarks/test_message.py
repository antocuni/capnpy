import pytest
import socket
import contextlib
from capnpy.buffered import BufferedSocket
from capnpy.benchmarks import support
from capnpy.benchmarks.test_benchmarks import get_obj, schema
from capnpy.benchmarks.test_buffered import TcpServer


class TestMessage(object):

    N = 50000

    @pytest.fixture(scope="class")
    def capnpfile(self, tmpdir_factory):
        tmpdir = tmpdir_factory.mktemp('capnpfile')
        tmpfile = tmpdir.join('mycapnpfile')
        obj = get_obj(support.Capnpy)
        with tmpfile.open('wb') as f:
            for i in range(self.N):
                obj.dump(f)
        return tmpfile

    def load_N(self, schema, open_connection):
        f = open_connection()
        for i in xrange(self.N):
            obj = schema.MyStruct.load(f)
        f.close()
        return obj

    @pytest.mark.benchmark(group="load")
    def test_load_from_file(self, schema, benchmark, capnpfile):
        if not hasattr(schema.MyStruct, 'load'):
            pytest.skip('N/A')
        #
        res = benchmark(self.load_N, schema, capnpfile.open)
        assert res.int64 == 100

    @pytest.mark.benchmark(group="load")
    def test_load_from_socket(self, schema, benchmark, capnpfile):
        if schema.__name__ not in ('Capnpy', 'PyCapnp'):
            pytest.skip('N/A')
        #
        host = TcpServer.host
        port = TcpServer.port
        def open_connection():
            sock = socket.create_connection((host, port))
            if schema.__name__ == 'Capnpy':
                sock = BufferedSocket(sock)
            return sock
        #
        with TcpServer(capnpfile) as server:
            # we do NOT want to measure the connection time. So, we open many
            # connections at once and let the benchmark use them one by one.
            # By default tcpserver accepts up to 40 connections
            pool = [open_connection() for _ in range(40)]
            next_connection = iter(pool).next
            res = benchmark(self.load_N, schema, next_connection)
            for conn in pool:
                conn.close()
        assert res.int64 == 100
