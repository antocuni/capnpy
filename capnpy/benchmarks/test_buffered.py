import pytest
import socket
import random
import subprocess
from cStringIO import StringIO
from capnpy.buffered import BufferedStream, BufferedSocket

@pytest.mark.usefixtures('initargs')
class TestBuffered(object):

    # apparently, the slowdown of makefile is not completely linear. E.g. by
    # using 20 MB I got a 20x slowdown compared to BufferedSocket, on PyPy.
    # Anyway, 1 MB should be enough to show that BufferedSocket is much faster
    SIZE = 1 * (1024*1024) # MB
    PORT = 5000

    @pytest.fixture
    def initargs(self, request, tmpdir):
        self.tmpdir = tmpdir
        # create the file to serve
        mystream = tmpdir.join('mystream')
        with mystream.open('wb') as f:
            buf = StringIO()
            for i in xrange(self.SIZE):
                ch = chr(random.randrange(255))
                f.write(ch)
        #
        # start tcpserver
        cmd = ['tcpserver', '127.0.0.1', str(self.PORT),
               'cat', str(mystream)]
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
    def test_BufferedSocket(self, benchmark):
        def open_connection():
            sock = socket.create_connection(('127.0.0.1', self.PORT))
            return BufferedSocket(sock)
        self.do_benchmark(benchmark, open_connection)

    @pytest.mark.benchmark(group="buffered")
    def test_BufferedStream(self, benchmark):
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
            return MyStream('127.0.0.1', self.PORT)
        self.do_benchmark(benchmark, open_connection)

    @pytest.mark.benchmark(group="buffered")
    def test_makefile(self, benchmark):
        def open_connection():
            sock = socket.create_connection(('127.0.0.1', self.PORT))
            return sock.makefile()
        self.do_benchmark(benchmark, open_connection)
