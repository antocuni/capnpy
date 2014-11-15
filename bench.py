import time
from collections import namedtuple
import capnpy_cffi
import capnpy_struct


def encode_rect():
    import capnp
    mod = capnp.load('point.capnp')
    r = mod.Rectangle.new_message()
    r.a.x = 1
    r.a.y = 2
    r.b.x = 3
    r.b.y = 4
    rbytes = r.to_bytes()
    print repr(rbytes)
    return rbytes

def encode_point():
    import capnp
    mod = capnp.load('point.capnp')
    p = mod.Point.new_message()
    p.x = 1
    p.y = 2
    rbytes = p.to_bytes()
    print repr(rbytes)
    return rbytes

#
# pycapnp doesn't work on pypy, so for the purpose of this benchmark we simply
# paste the already-encoded bytes
#
#rect_bytes = encode_rect()
#point_bytes = encode_point()
rect_bytes = '\x00\x00\x00\x00\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x04\x00\x00\x00\x02\x00\x00\x00\x08\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00'
point_bytes = '\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00'


PyPoint = namedtuple('PyPoint', ['x', 'y'])
PyRect = namedtuple('PyRect', ['a', 'b'])


def bench_rect():
    print 'Rectangle benchmark:'
    rlist = [PyRect(PyPoint(1, 2), PyPoint(3, 4)) for i in range(N)]
    res = 0
    a = time.time()
    for r in rlist:
        res += r.a.x + r.a.y + r.b.x + r.b.y
    b = time.time()
    print '  namedtuple:            %9.4f ms (res=%d)' % ((b-a)*1000, res)

    rlist = [capnpy_struct.decode_message(rect_bytes, capnpy_struct.Rectangle)
             for i in range(N)]
    res = 0
    a = time.time()
    for r in rlist:
        res += r.a.x + r.a.y + r.b.x + r.b.y
    b = time.time()
    print '  capnpy_struct (byref): %9.4f ms (res=%d)' % ((b-a)*1000, res)

    rlist = [capnpy_struct.decode_message(rect_bytes, capnpy_struct.Rectangle)
             for i in range(N)]
    res = 0
    a = time.time()
    for r in rlist:
        res += r.a_byval.x + r.a_byval.y + r.b_byval.x + r.b_byval.y
    b = time.time()
    print '  capnpy_struct (byval): %9.4f ms (res=%d)' % ((b-a)*1000, res)


    rlist = [capnpy_cffi.decode_message(rect_bytes, capnpy_cffi.Rectangle)
             for i in range(N)]
    res = 0
    a = time.time()
    for r in rlist:
        res += r.a.x + r.a.y + r.b.x + r.b.y
    b = time.time()
    print '  capnpy_cffi:           %9.4f ms (res=%d)' % ((b-a)*1000, res)

    try:
        import capnp
    except ImportError:
        return
    mod = capnp.load('point.capnp')
    plist = [mod.Rectangle.from_bytes(rect_bytes) for i in range(N)]
    res = 0
    a = time.time()
    for r in rlist:
        res += r.a.x + r.a.y + r.b.x + r.b.y
    b = time.time()
    print '  pycapnp:       %9.4f ms (res=%d)' % ((b-a)*1000, res)


def bench_point():
    print 'Point benchmark:'
    plist = [PyPoint(1, 2) for i in range(N)]
    res = 0
    a = time.time()
    for p in plist:
        res += p.x + p.y
    b = time.time()
    print '  namedtuple:            %9.4f ms (res=%d)' % ((b-a)*1000, res)

    plist = [capnpy_struct.decode_message(point_bytes, capnpy_struct.Point)
             for i in range(N)]
    res = 0
    a = time.time()
    for p in plist:
        res += p.x + p.y
    b = time.time()
    print '  capnpy_struct:         %9.4f ms (res=%d)' % ((b-a)*1000, res)

    plist = [capnpy_cffi.decode_message(point_bytes, capnpy_cffi.Point)
             for i in range(N)]
    res = 0
    a = time.time()
    for p in plist:
        res += p.x + p.y
    b = time.time()
    print '  capnpy_cffi:           %9.4f ms (res=%d)' % ((b-a)*1000, res)

    try:
        import capnp
    except ImportError:
        return
    mod = capnp.load('point.capnp')
    plist = [mod.Point.from_bytes(point_bytes) for i in range(N)]
    res = 0
    a = time.time()
    for p in plist:
        res += p.x + p.y
    b = time.time()
    print '  pycapnp:       %9.4f ms (res=%d)' % ((b-a)*1000, res)



N = 100000
print '<first run>'
bench_point()
print
bench_rect()
print
print
print '<second run>'
bench_point()
print
bench_rect()
