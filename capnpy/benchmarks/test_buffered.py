import pytest
import socket
import random
import subprocess
from cStringIO import StringIO
from capnpy.buffered import BufferedStream, BufferedSocket

class TestBuffered(object):

    # apparently, the slowdown of makefile is not completely linear. E.g. by
    # using 20 MB I got a 20x slowdown compared to BufferedSocket, on PyPy.
    # Anyway, 1 MB should be enough to show that BufferedSocket is much faster
    SIZE = 1 * (1024*1024) # MB

    @pytest.fixture(scope='class')
    def server(self, request, tmpdir_factory):
        host = '127.0.0.1'
        port = '5000'
        tmpdir = tmpdir_factory.mktemp('buffered')
        # create the file to serve
        mystream = tmpdir.join('mystream')
        with mystream.open('wb') as f:
            buf = StringIO()
            for i in xrange(self.SIZE):
                ch = chr(random.randrange(255))
                f.write(ch)
        #
        # start tcpserver
        cmd = ['tcpserver', host, port, 'cat', str(mystream)]
        p = subprocess.Popen(cmd)
        #
        # stop tcpserver
        def finalize():
            try:
                p.kill()
            except OSError:
                pass
            if p.returncode is None:
                p.communicate()
        request.addfinalizer(finalize)
        #
        return host, port

    def do_benchmark(self, benchmark, open_connection):
        def count_bytes():
            f = open_connection()
            tot = 0
            while True:
                s = f.read(1)
                if s == '':
                    break
                tot += len(s)
            return tot

        res = benchmark(count_bytes)
        assert res == self.SIZE

    @pytest.mark.benchmark(group="buffered")
    def test_BufferedSocket(self, benchmark, server):
        def open_connection():
            host, port = server
            sock = socket.create_connection((host, port))
            return BufferedSocket(sock)
        self.do_benchmark(benchmark, open_connection)

    @pytest.mark.benchmark(group="buffered")
    def test_BufferedStream(self, benchmark, server):
        # this is like BufferedSocket, but with the overhead that _readchunk
        # is written in Python instead of Cython; this simulates what happens
        # if an user of capnpy wants to wrap its own stream reader
        class MyStream(BufferedStream):
            def __init__(self, host, port):
                super(MyStream, self).__init__()
                self.sock = socket.create_connection((host, port))

            def _readchunk(self):
                return self.sock.recv(8192)

        def open_connection():
            host, port = server
            return MyStream(host, port)
        self.do_benchmark(benchmark, open_connection)

    @pytest.mark.benchmark(group="buffered")
    def test_makefile(self, benchmark, server):
        def open_connection():
            host, port = server
            sock = socket.create_connection((host, port))
            return sock.makefile()
        self.do_benchmark(benchmark, open_connection)
