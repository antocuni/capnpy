from capnpy.filelike import FileLike

class BufferedSocket(FileLike):

    def __init__(self, sock, bufsize=8192):
        self.sock = sock
        self.bufsize = bufsize
        self.buf = b''
        self.i = 0

    def _fillbuf(self, size):
        parts = [self.buf[self.i:]]
        total = len(parts[0])
        while total < size:
            part = self.sock.recv(self.bufsize)
            if part == b'':
                break # connection closed, no more data
            total += len(part)
            parts.append(part)
        #
        self.buf = b''.join(parts)
        self.i = 0

    def read(self, size):
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
            part = self.sock.recv(self.bufsize)
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
