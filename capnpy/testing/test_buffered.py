import pytest
from capnpy.buffered import BufferedStream, BufferedSocket, StringBuffer

class FakeSocket(object):

    def __init__(self, *packets):
        self.packets = iter(packets)
        self.received = ''

    def recv(self, size):
        try:
            return next(self.packets)
        except StopIteration:
            return ''

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
            return ''


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
        stream = self.get_stream('aaaabbbbccccdddd')
        assert stream.read(4) == 'aaaa'
        assert stream.read(4) == 'bbbb'
        assert stream.read(4) == 'cccc'
        assert stream.read(4) == 'dddd'
        assert stream.read(4) == ''

    def test_read_at_boundary_of_buffer(self):
        stream = self.get_stream('aaaa', 'bbbb')
        assert stream.read(2) == 'aa'
        assert stream.read(4) == 'aabb'
        assert stream.read(2) == 'bb'
        assert stream.read(4) == ''

    def test_not_enough_bytes_at_the_end(self):
        stream = self.get_stream('aaaabbbbccccdd')
        assert stream.read(4) == 'aaaa'
        assert stream.read(4) == 'bbbb'
        assert stream.read(4) == 'cccc'
        assert stream.read(4) == 'dd'
        assert stream.read(4) == ''

    def test_recv_returns_less_than_requested(self):
        stream = self.get_stream('aaaa', 'bbbb', 'cccc', 'dddd')
        assert stream.read(6) == 'aaaabb'
        assert stream.read(4) == 'bbcc'
        assert stream.read(4) == 'ccdd'
        assert stream.read(4) == 'dd'
        assert stream.read(4) == ''

    def test_readline(self):
        stream = self.get_stream('aaaa\nbbbb\ncccc\ndddd')
        assert stream.readline() == 'aaaa\n'
        assert stream.readline() == 'bbbb\n'
        assert stream.readline() == 'cccc\n'
        assert stream.readline() == 'dddd'
        assert stream.readline() == ''

    def test_readline_corner_cases(self):
        stream = self.get_stream('aaaa\n', 'bb', 'bb', '\ncc', 'cc\ndd', 'dd')
        assert stream.readline() == 'aaaa\n'
        assert stream.readline() == 'bbbb\n'
        assert stream.readline() == 'cccc\n'
        assert stream.readline() == 'dddd'
        assert stream.readline() == ''

    def test_read_and_readline(self):
        stream = self.get_stream('aaaa\nbbbb\ncccc\ndddd')
        assert stream.read(2) == 'aa'
        assert stream.readline() == 'aa\n'
        assert stream.readline() == 'bbbb\n'
        assert stream.read(5) == 'cccc\n'
        assert stream.readline() == 'dddd'
        assert stream.readline() == ''
        assert stream.read(2) == ''

    def test_read_all(self):
        stream = self.get_stream('aaaa', 'bbbb', 'cccc', 'dddd')
        assert stream.read() == 'aaaabbbbccccdddd'
        assert stream.read(1) == ''
        assert stream.read() == ''

    def test_read_all_after_read(self):
        stream = self.get_stream('aaaa', 'bbbb', 'cccc', 'dddd')
        assert stream.read(2) == 'aa' # leave 'aa' in the buffer
        assert stream.read() == 'aabbbbccccdddd'
        assert stream.read(1) == ''
        assert stream.read() == ''

    def test_write(self):
        if self.param != 'BufferedSocket':
            return
        sock = FakeSocket()
        bufsock = BufferedSocket(sock)
        bufsock.write('hello ')
        bufsock.write('world')
        assert sock.received == ''
        bufsock.flush()
        assert sock.received == 'hello world'
        bufsock.write(' foobar')
        assert sock.received == 'hello world'
        bufsock.flush()
        assert sock.received == 'hello world foobar'


class TestStringBuffer(object):

    def test_read(self):
        f = StringBuffer('aaaabbbb')
        assert f.read(4) == 'aaaa'
        assert f.read(2) == 'bb'
        assert f.read(2) == 'bb'
        assert f.read(4) == ''
        assert f.read(4) == ''

    def test_read_all(self):
        f = StringBuffer('aaaabbbb')
        assert f.read(2) == 'aa'
        assert f.read() == 'aabbbb'
        assert f.read() == ''

    def test_readline(self):
        f = StringBuffer('aaaa\nbbbb\ncccc\ndddd')
        assert f.readline() == 'aaaa\n'
        assert f.readline() == 'bbbb\n'
        assert f.readline() == 'cccc\n'
        assert f.readline() == 'dddd'
        assert f.readline() == ''

    def test_read_and_readline(self):
        f = StringBuffer('aaaa\nbbbb\ncccc\ndddd')
        assert f.read(2) == 'aa'
        assert f.readline() == 'aa\n'
        assert f.readline() == 'bbbb\n'
        assert f.read(5) == 'cccc\n'
        assert f.readline() == 'dddd'
        assert f.readline() == ''
        assert f.read(2) == ''
