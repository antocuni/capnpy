from __future__ import print_function
import sys
import struct
from pypytools.jitview import Color
from capnpy import ptr

COLORS = [Color.darkred, Color.darkgreen, Color.brown,
          Color.darkblue, Color.purple, Color.teal]

def print_buffer(buf, **kwds):
    p = BufferPrinter(buf)
    p.printbuf(end=None, **kwds)

class BufferPrinter(object):

    def __init__(self, buf, stream=None):
        self.buf = buf
        self.stream = stream or sys.stdout

    def pyrepr(self, s):
        ch = s[0]
        if ch.isalnum():
            return repr(s)
        else:
            body = ''.join((r'\x%02x' % ord(ch)) for ch in s)
            return "'%s'" % body

    def hex(self, s):
        digits = []
        for ch in s:
            if ch == '\x00':
                digits.append(Color.set(Color.lightgray, '00'))
            else:
                digits.append('%02X' % ord(ch))
        return ' '.join(digits)

    def addr(self, x):
        color = (x/8) % len(COLORS)
        color = COLORS[color]
        return Color.set(color, '%d' % x)

    def string(self, s):
        def printable(ch):
            if 32 <= ord(ch) <= 127:
                return ch
            else:
                return Color.set(Color.lightgray, '.')
        return ''.join(map(printable, s))

    def int64(self, s):
        val = struct.unpack('q', s)[0]
        if val < 65536:
            return str(val)
        else:
            return Color.set(Color.lightgray, str(val))

    def float64(self, s):
        d = struct.unpack('d', s)[0]
        s = str(d).rjust(9)
        if len(s) > 9:
            s = '{:<9.2E}'.format(d)
            return Color.set(Color.lightgray, s)
        else:
            return '{:<9}'.format(s)

    def ptr(self, offset, s):
        p = struct.unpack('q', s)[0]
        if ptr.kind(p) not in (ptr.STRUCT, ptr.LIST, ptr.FAR):
            return ' ' * 25
        #
        # try to display only "reasonable" ptrs; if the fields are too big, it
        # probably means that the current word is not a pointer
        def if_in_range(x, min, max):
            if min <= x < max:
                return str(x)
            else:
                return '?'
        #
        if p == 0:
            return  'NULL'.ljust(25)
        if ptr.kind(p) == ptr.STRUCT:
            descr = 'struct {:>4} {:>3}'.format(
                if_in_range(ptr.struct_data_size(p), 0, 100),
                if_in_range(ptr.struct_ptrs_size(p), 0, 100))

        elif ptr.kind(p) == ptr.LIST:
            tag = '<%s>' % self._list_tag(ptr.list_size_tag(p))
            descr = 'list{:<5} {:>5}'.format(
                tag,
                if_in_range(ptr.list_item_count(p), 0, 65536))

        elif ptr.kind(p) == ptr.FAR:
            descr = 'far {:>7} {:>3}'.format(
                ptr.far_landing_pad(p),
                if_in_range(ptr.far_target(p), 0, 100))
        else:
            descr = 'unknown ptr '
        #
        if -1000 < ptr.offset(p) < 1000:
            dest = ptr.deref(p, offset)
            dest = self.addr(dest)
            dest = dest.ljust(16)
        else:
            dest = '?     '
        line = '{0} to {1}'.format(descr, dest)
        if '?' in line:
            return Color.set(Color.lightgray, line)
        else:
            return line

    def _list_tag(self, tag):
        tags = ('v', 'bit', '8', '16', '32', '64', 'ptr', 'cmp')
        try:
            return tags[tag]
        except IndexError:
            return '?'

    def line(self, offset, line):
        addr = self.addr(offset)
        hex = self.hex(line)
        string = self.string(line)
        int64 = self.int64(line)
        float64 = self.float64(line)
        ptr = self.ptr(offset, line)
        # addr is aligned to 16 because 11 chars are ANSI codes for setting colors
        fmt = '{addr:>16}:  {hex}  {string:>8}  {ptr} {float64}  {int64}'
        return fmt.format(**locals())

    def printbuf(self, start=0, end=None, human=True):
        if human:
            fmt = '{addr:>5}  {hex:24}  {string:8}  {ptr:23} {float64:>11}  {int64}'
            header = fmt.format(addr='Offset', hex=' Hex view', string='ASCII',
                                ptr='Pointer', float64='float64', int64='int64')
            print(Color.set(Color.yellow, header))

        if end is None:
            end = len(self.buf)
        for i in range(start/8, end/8):
            addr = i*8
            line = self.buf[i*8:i*8+8]
            if human:
                print(self.line(addr, line), file=self.stream)
            else:
                print('%5d: %s' % (addr, self.pyrepr(line)), file=self.stream)


if __name__ == '__main__':
    ## buf = ('\x04\x00\x00\x00\x02\x00\x00\x00'    # ptr to a
    ##        '\x08\x00\x00\x00\x02\x00\x00\x00'    # ptr to b
    ##        '\x01\x00\x00\x00\x00\x00\x00\x00'    # a.x == 1
    ##        '\x02\x00\x00\x00\x00\x00\x00\x00'    # a.y == 2
    ##        '\x03\x00\x00\x00\x00\x00\x00\x00'    # b.x == 3
    ##        '\x04\x00\x00\x00\x00\x00\x00\x00'    # b.y == 4
    ##        '\x01\x00\x00\x00\x82\x00\x00\x00'    # ptrlist
    ##        'hello capnproto\0')                  # string
    pipe =  '--pipe' in sys.argv
    buf = sys.stdin.read()
    if pipe:
        out = sys.stderr
    else:
        out = sys.stdout
    p = BufferPrinter(buf, stream=out)
    p.printbuf(human=True)
    if pipe:
        sys.stdout.write(buf)
