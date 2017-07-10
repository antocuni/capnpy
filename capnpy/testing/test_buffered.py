import pytest
from capnpy.buffered import BufferedStream, BufferedSocket, StringBuffer

class FakeSocket(object):

    def __init__(self, *packets):
        self.packets = iter(packets)
        self.received = b''

    def recv(self, size):
        try:
            return next(self.packets)
        except StopIteration:
            return b''

    def sendall(self, data):
        self.received += data


class MyBufferedStream(BufferedStream):

    def __init__(self, *packets):
        super(MyBufferedStream, self).__init__()
        self.packets = iter(packets)

    def _readchunk(self):
        try:
            return next(self.packets)
        except StopIteration:
            return b''


@pytest.mark.usefixtures('initargs')
class TestBufferedStream(object):

    @pytest.fixture(params=['BufferedStream', 'BufferedSocket'])
    def initargs(self, request):
        self.param = request.param

    def get_stream(self, *packets):
        if self.param == 'BufferedStream':
            return MyBufferedStream(*packets)
        elif self.param == 'BufferedSocket':
            sock = FakeSocket(*packets)
            return BufferedSocket(sock)
        assert False

    def test_buffering(self):
        stream = self.get_stream(b'aaaabbbbccccdddd')
        assert stream.read(4) == b'aaaa'
        assert stream.read(4) == b'bbbb'
        assert stream.read(4) == b'cccc'
        assert stream.read(4) == b'dddd'
        assert stream.read(4) == b''

    def test_read_at_boundary_of_buffer(self):
        stream = self.get_stream(b'aaaa', b'bbbb')
        assert stream.read(2) == b'aa'
        assert stream.read(4) == b'aabb'
        assert stream.read(2) == b'bb'
        assert stream.read(4) == b''

    def test_not_enough_bytes_at_the_end(self):
        stream = self.get_stream(b'aaaabbbbccccdd')
        assert stream.read(4) == b'aaaa'
        assert stream.read(4) == b'bbbb'
        assert stream.read(4) == b'cccc'
        assert stream.read(4) == b'dd'
        assert stream.read(4) == b''

    def test_recv_returns_less_than_requested(self):
        stream = self.get_stream(b'aaaa', b'bbbb', b'cccc', b'dddd')
        assert stream.read(6) == b'aaaabb'
        assert stream.read(4) == b'bbcc'
        assert stream.read(4) == b'ccdd'
        assert stream.read(4) == b'dd'
        assert stream.read(4) == b''

    def test_readline(self):
        stream = self.get_stream(b'aaaa\nbbbb\ncccc\ndddd')
        assert stream.readline() == b'aaaa\n'
        assert stream.readline() == b'bbbb\n'
        assert stream.readline() == b'cccc\n'
        assert stream.readline() == b'dddd'
        assert stream.readline() == b''

    def test_readline_corner_cases(self):
        stream = self.get_stream(b'aaaa\n', b'bb', b'bb', b'\ncc', b'cc\ndd', b'dd')
        assert stream.readline() == b'aaaa\n'
        assert stream.readline() == b'bbbb\n'
        assert stream.readline() == b'cccc\n'
        assert stream.readline() == b'dddd'
        assert stream.readline() == b''

    def test_read_and_readline(self):
        stream = self.get_stream(b'aaaa\nbbbb\ncccc\ndddd')
        assert stream.read(2) == b'aa'
        assert stream.readline() == b'aa\n'
        assert stream.readline() == b'bbbb\n'
        assert stream.read(5) == b'cccc\n'
        assert stream.readline() == b'dddd'
        assert stream.readline() == b''
        assert stream.read(2) == b''

    def test_read_all(self):
        stream = self.get_stream(b'aaaa', b'bbbb', b'cccc', b'dddd')
        assert stream.read() == b'aaaabbbbccccdddd'
        assert stream.read(1) == b''
        assert stream.read() == b''

    def test_read_all_after_read(self):
        stream = self.get_stream(b'aaaa', b'bbbb', b'cccc', b'dddd')
        assert stream.read(2) == b'aa' # leave 'aa' in the buffer
        assert stream.read() == b'aabbbbccccdddd'
        assert stream.read(1) == b''
        assert stream.read() == b''

    def test_write(self):
        if self.param != 'BufferedSocket':
            return
        sock = FakeSocket()
        bufsock = BufferedSocket(sock)
        bufsock.write(b'hello ')
        bufsock.write(b'world')
        assert sock.received == b''
        bufsock.flush()
        assert sock.received == b'hello world'
        bufsock.write(b' foobar')
        assert sock.received == b'hello world'
        bufsock.flush()
        assert sock.received == b'hello world foobar'


class TestStringBuffer(object):

    def test_read(self):
        f = StringBuffer(b'aaaabbbb')
        assert f.read(4) == b'aaaa'
        assert f.read(2) == b'bb'
        assert f.read(2) == b'bb'
        assert f.read(4) == b''
        assert f.read(4) == b''

    def test_read_all(self):
        f = StringBuffer(b'aaaabbbb')
        assert f.read(2) == b'aa'
        assert f.read() == b'aabbbb'
        assert f.read() == b''

    def test_readline(self):
        f = StringBuffer(b'aaaa\nbbbb\ncccc\ndddd')
        assert f.readline() == b'aaaa\n'
        assert f.readline() == b'bbbb\n'
        assert f.readline() == b'cccc\n'
        assert f.readline() == b'dddd'
        assert f.readline() == b''

    def test_read_and_readline(self):
        f = StringBuffer(b'aaaa\nbbbb\ncccc\ndddd')
        assert f.read(2) == b'aa'
        assert f.readline() == b'aa\n'
        assert f.readline() == b'bbbb\n'
        assert f.read(5) == b'cccc\n'
        assert f.readline() == b'dddd'
        assert f.readline() == b''
        assert f.read(2) == b''
