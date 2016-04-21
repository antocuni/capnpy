from capnpy.buffered import BufferedSocket, StringBuffer

class FakeSocket(object):

    def __init__(self, *packets):
        self.packets = iter(packets)

    def recv(self, size):
        try:
            return next(self.packets)
        except StopIteration:
            return ''


class TestBufferedSocket(object):
    
    def test_buffering(self):
        sock = FakeSocket('aaaabbbbccccdddd')
        sock = BufferedSocket(sock)
        assert sock.read(4) == 'aaaa'
        assert sock.read(4) == 'bbbb'
        assert sock.read(4) == 'cccc'
        assert sock.read(4) == 'dddd'
        assert sock.read(4) == ''

    def test_read_at_boundary_of_buffer(self):
        sock = FakeSocket('aaaa', 'bbbb')
        sock = BufferedSocket(sock)
        assert sock.read(2) == 'aa'
        assert sock.read(4) == 'aabb'
        assert sock.read(2) == 'bb'
        assert sock.read(4) == ''

    def test_not_enough_bytes_at_the_end(self):
        sock = FakeSocket('aaaabbbbccccdd')
        sock = BufferedSocket(sock)
        assert sock.read(4) == 'aaaa'
        assert sock.read(4) == 'bbbb'
        assert sock.read(4) == 'cccc'
        assert sock.read(4) == 'dd'
        assert sock.read(4) == ''

    def test_recv_returns_less_than_requested(self):
        sock = FakeSocket('aaaa', 'bbbb', 'cccc', 'dddd')
        sock = BufferedSocket(sock)
        assert sock.read(6) == 'aaaabb'
        assert sock.read(4) == 'bbcc'
        assert sock.read(4) == 'ccdd'
        assert sock.read(4) == 'dd'
        assert sock.read(4) == ''

    def test_readline(self):
        sock = FakeSocket('aaaa\nbbbb\ncccc\ndddd')
        sock = BufferedSocket(sock)
        assert sock.readline() == 'aaaa\n'
        assert sock.readline() == 'bbbb\n'
        assert sock.readline() == 'cccc\n'
        assert sock.readline() == 'dddd'
        assert sock.readline() == ''

    def test_readline_corner_cases(self):
        sock = FakeSocket('aaaa\n', 'bb', 'bb', '\ncc', 'cc\ndd', 'dd')
        sock = BufferedSocket(sock)
        assert sock.readline() == 'aaaa\n'
        assert sock.readline() == 'bbbb\n'
        assert sock.readline() == 'cccc\n'
        assert sock.readline() == 'dddd'
        assert sock.readline() == ''

    def test_read_and_readline(self):
        sock = FakeSocket('aaaa\nbbbb\ncccc\ndddd')
        sock = BufferedSocket(sock)
        assert sock.read(2) == 'aa'
        assert sock.readline() == 'aa\n'
        assert sock.readline() == 'bbbb\n'
        assert sock.read(5) == 'cccc\n'
        assert sock.readline() == 'dddd'
        assert sock.readline() == ''
        assert sock.read(2) == ''

    def test_read_all(self):
        sock = FakeSocket('aaaa', 'bbbb', 'cccc', 'dddd')
        sock = BufferedSocket(sock)
        assert sock.read() == 'aaaabbbbccccdddd'
        assert sock.read(1) == ''
        assert sock.read() == ''

    def test_read_all_after_read(self):
        sock = FakeSocket('aaaa', 'bbbb', 'cccc', 'dddd')
        sock = BufferedSocket(sock)
        assert sock.read(2) == 'aa' # leave 'aa' in the buffer
        assert sock.read() == 'aabbbbccccdddd'
        assert sock.read(1) == ''
        assert sock.read() == ''


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
