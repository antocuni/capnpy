import pytest
import socket
import contextlib
from capnpy.buffered import BufferedSocket
from capnpy.benchmarks import support
from capnpy.benchmarks.test_benchmarks import get_obj, schema
from capnpy.benchmarks.test_buffered import TcpServer


class TestLoad(object):

    # we need a huge N because pytest_benchmark because else the time is
    # dominated by open_connection() in test_load_from_socket
    N = 500000

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
            res = benchmark(self.load_N, schema, open_connection)
        assert res.int64 == 100


class TestDump(object):

    N = 2000

    @pytest.mark.benchmark(group="dumps")
    def test_copy_buffer(self, schema, benchmark):
        # this is not really a dumps, but it is used as a baseline to compare
        # the performance
        if schema.__name__ != 'Capnpy':
            pytest.skip('N/A')
        #
        def dumps_N(obj):
            myobjs = (obj, obj)
            res = 0
            for i in range(self.N):
                obj = myobjs[i%2]
                res = obj._seg.buf[:]
            return res
        #
        obj = get_obj(schema)
        res = benchmark(dumps_N, obj)
        assert type(res) is str

    @pytest.mark.benchmark(group="dumps")
    def test_dumps(self, schema, benchmark):
        if schema.__name__ != 'Capnpy':
            pytest.skip('N/A')
        #
        def dumps_N(obj):
            myobjs = (obj, obj)
            res = 0
            for i in range(self.N):
                obj = myobjs[i%2]
                res = obj.dumps()
            return res
        #
        obj = get_obj(schema)
        res = benchmark(dumps_N, obj)
        assert type(res) is str

    @pytest.mark.benchmark(group="dumps")
    def test_dumps_not_compact(self, schema, benchmark):
        if schema.__name__ != 'Capnpy':
            pytest.skip('N/A')
        #
        def dumps_N(obj):
            myobjs = (obj, obj)
            res = 0
            for i in range(self.N):
                obj = myobjs[i%2]
                res = obj.dumps()
            return res
        #
        obj = get_obj(schema)
        container = schema.MyStructContainer(items=[obj, obj])
        obj0 = container.items[0]
        assert not obj0._is_compact()
        res = benchmark(dumps_N, obj0)
        assert type(res) is str

    @pytest.mark.benchmark(group="dumps")
    def test_dumps_not_compact_no_fastpath(self, schema, benchmark):
        if schema.__name__ != 'Capnpy':
            pytest.skip('N/A')
        #
        def dumps_N(obj):
            myobjs = (obj, obj)
            res = 0
            for i in range(self.N):
                obj = myobjs[i%2]
                res = obj.dumps(fastpath=False)
            return res
        #
        obj = get_obj(schema)
        container = schema.MyStructContainer(items=[obj, obj])
        obj0 = container.items[0]
        assert not obj0._is_compact()
        res = benchmark(dumps_N, obj0)
        assert type(res) is str
