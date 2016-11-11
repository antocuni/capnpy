from capnpy.filelike import FileLike

class BufferedStream(FileLike):
    """
    file-like interface to read data from a generic stream in a buffered way.

    This is an abstract class: to use it, you need to subclass and implement
    the _readchunk method; _readchunk is supposed to be slowish and to
    return a big chunk of data, which will be kept in a buffer; read() and
    readline() reads from it.
    """

    def __init__(self):
        self.buf = b''
        self.i = 0

    def _readchunk(self):
        raise NotImplementedError

    def _fillbuf(self, size):
        parts = [self.buf[self.i:]]
        total = len(parts[0])
        while total < size:
            part = self._readchunk()
            if part == b'':
                break # connection closed, no more data
            total += len(part)
            parts.append(part)
        #
        self.buf = b''.join(parts)
        self.i = 0

    def _readall(self):
        parts = [self.buf[self.i:]]
        self.buf = b''
        self.i = 0
        while True:
            part = self._readchunk()
            if part == b'':
                break
            parts.append(part)
        return b''.join(parts)

    def read(self, size=-1):
        if size == -1:
            return self._readall()
        i = self.i
        j = i + size
        if len(self.buf) < j:
            # not enough data in the buffer, let's refill it
            self._fillbuf(size)
            self.i = size
            return self.buf[:size]
        #
        # data already in the buffer, fast path
        self.i = j
        return self.buf[i:j]

    def readline(self):
        i = self.i
        j = self.buf.find(b'\n', i)
        if j != -1:
            # fast path: already in the buffer, just return it
            self.i = j+1
            return self.buf[i:j+1]
        #
        # slow path, read until we find a newline
        parts = [self.buf[i:]]
        self.buf = b''
        self.i = 0
        while True:
            part = self._readchunk()
            if part == b'':
                break # connection closed, no more data
            #
            j = part.find(b'\n')
            if j != -1: # finally found a newline
                parts.append(part[:j+1]) # read until the newline
                self.buf = part[j+1:]    # and keep the rest in the buffer
                self.i = 0
                break
            else:
                parts.append(part)
        #
        return b''.join(parts)

    def write(self, data):
        raise NotImplementedError

    def flush(self):
        raise NotImplementedError


class BufferedSocket(BufferedStream):
    """
    file-like interface to read data from a socket in a buffered way.
    Similar to socket.makefile(), but read() is much faster. See:
    https://bitbucket.org/pypy/pypy/issues/2272/socket_fileobjectread-horribly-slow

    write() and flush() are supported, although they are not particularly
    optimized: write() always appends the data to its iternal buffer, which is
    sent only when calling flush().
    """

    def __init__(self, sock, bufsize=8192):
        super(BufferedSocket, self).__init__()
        self.sock = sock
        self.bufsize = bufsize
        self.wbuf = []

    def _readchunk(self):
        return self.sock.recv(self.bufsize)

    def write(self, data):
        self.wbuf.append(data)

    def flush(self):
        data = ''.join(self.wbuf)
        self.sock.sendall(data)
        self.wbuf = []

    def close(self):
        self.sock.close()


class StringBuffer(FileLike):
    """
    file-like interface to read data out of a string. Like StringIO, but since
    it inherits from FileLike, it can be used by message.load() more
    efficiently.
    """

    def __init__(self, s):
        self.s = s
        self.i = 0

    def read(self, size=-1):
        i = self.i
        if size == -1:
            self.i = len(self.s)
            return self.s[i:]
        else:
            j = i + size
            self.i = j
            return self.s[i:j]

    def readline(self):
        i = self.i
        j = self.s.find('\n', self.i)+1
        if j == 0:
            self.i = len(self.s)
            return self.s[i:]
        else:
            self.i = j
            return self.s[i:j]

    def tell(self):
        return self.i
