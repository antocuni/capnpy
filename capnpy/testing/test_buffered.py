from capnpy.buffered import BufferedSocket

class FakeSocket(object):

    def __init__(self, *packets):
        self.packets = iter(packets)

    def recv(self, size):
        try:
            return next(self.packets)
        except StopIteration:
            return ''

            
def test_buffering():
    sock = FakeSocket('aaaabbbbccccdddd')
    sock = BufferedSocket(sock)
    assert sock.read(4) == 'aaaa'
    assert sock.read(4) == 'bbbb'
    assert sock.read(4) == 'cccc'
    assert sock.read(4) == 'dddd'
    assert sock.read(4) == ''

def test_read_at_boundary_of_buffer():
    sock = FakeSocket('aaaa', 'bbbb')
    sock = BufferedSocket(sock)
    assert sock.read(2) == 'aa'
    assert sock.read(4) == 'aabb'
    assert sock.read(2) == 'bb'
    assert sock.read(4) == ''
    
def test_not_enough_bytes_at_the_end():
    sock = FakeSocket('aaaabbbbccccdd')
    sock = BufferedSocket(sock)
    assert sock.read(4) == 'aaaa'
    assert sock.read(4) == 'bbbb'
    assert sock.read(4) == 'cccc'
    assert sock.read(4) == 'dd'
    assert sock.read(4) == ''

def test_recv_returns_less_than_requested():
    sock = FakeSocket('aaaa', 'bbbb', 'cccc', 'dddd')
    sock = BufferedSocket(sock)
    assert sock.read(6) == 'aaaabb'
    assert sock.read(4) == 'bbcc'
    assert sock.read(4) == 'ccdd'
    assert sock.read(4) == 'dd'
    assert sock.read(4) == ''
