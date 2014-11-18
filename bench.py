import sys
import time
from collections import namedtuple
import zlib
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
    p.name = 'this is a point'
    rbytes = p.to_bytes()
    print repr(rbytes)
    return rbytes

def encode_polygon():
    import capnp
    mod = capnp.load('point.capnp')
    poly = mod.Polygon.new_message()
    poly.init('points', 100)
    for i, p in enumerate(poly.points):
        p.x = i
        p.y = i
    poly_bytes = poly.to_bytes()
    print repr(poly_bytes)
    return poly_bytes
    

#
# pycapnp doesn't work on pypy, so for the purpose of this benchmark we simply
# paste the already-encoded bytes
#
#rect_bytes = encode_rect()
#point_bytes = encode_point()
#poly_bytes = encode_polygon()

rect_bytes = '\x00\x00\x00\x00\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x04\x00\x00\x00\x02\x00\x00\x00\x08\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00'
point_bytes = '\x00\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x02\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x82\x00\x00\x00this is a point\x00'
poly_bytes = zlib.decompress('x\x9ce\xc6\xc5A\x03\x00\x14D\xc1\x9f\x00\xc1!\xb8[pww\r\xee\xee\xd2\x10}\xd1\x14\xb9p\x19\xde\x1ef#"~\xe2\xafDn\x11\xd9T\xc4w\xee$\xe3\x7f\tLb\x1e\xe6c\x01\xa6\xb0\x10\x8b\xb0\x18K\xb0\x14\xcb\xb0\x1c+\xb0\x12\xd3X\x85\xd5X\x83\xb5X\x87\xf5\xd8\x80\x8d\xd8\x84\xcd\xd8\x82\xad\xd8\x86\xed\xd8\x81\x9d\xd8\x85\x19\xec\xc6\x1e\xec\xc5>\xec\xc7\x01\x1c\xc4!\x1c\xc6\x11\x1c\xc51\x1c\xc7\t\x9c\xc4)\x9c\xc6\x19\x9c\xc59\x9c\xc7\x05\\\xc4%\\\xc6\x15\\\xc55\\\xc7\r\xdc\xc4-\xdc\xc6\x1d\xdc\xc5=\xcc\xe2>\x1e\xe0!\x1e\xe11\x9e\xe0)\x9e\xe19^\xe0%^\xe15\xde\xe0-\xde\xe1=>\xe0#>\xe13\xbe\xe0+\xbe\xe1;~\xe0\'~\xe1/h\x00(Z')


PyPoint = namedtuple('PyPoint', ['x', 'y', 'name'])
PyRect = namedtuple('PyRect', ['a', 'b'])
PyPoly = namedtuple('PyPoly', ['points'])

def bench_rect():
    print 'Rectangle benchmark:'
    rlist = [PyRect(PyPoint(1, 2, ''), PyPoint(3, 4, '')) for i in range(N)]
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

    return
    # the _cffi and pycapnp versions are not interesting at the moment
    
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
    print '  pycapnp:               %9.4f ms (res=%d)' % ((b-a)*1000, res)


def bench_point():
    print 'Point benchmark:'
    plist = [PyPoint(1, 2, '') for i in range(N)]
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
    print '  pycapnp:               %9.4f ms (res=%d)' % ((b-a)*1000, res)


def bench_poly():
    print 'Polygon benchmark:'
    plist = [PyPoly(points=[PyPoint(i, i, '') for i in range(100)]) for j in range(N/100)]
    res = 0
    a = time.time()
    for poly in plist:
        for p in poly.points:
            res += p.x + p.y
    b = time.time()
    print '  namedtuple:            %9.4f ms (res=%d)' % ((b-a)*1000, res)

    
    plist = [capnpy_struct.decode_message(poly_bytes, capnpy_struct.Polygon)
             for i in range(N/100)]
    res = 0
    a = time.time()
    for poly in plist:
        for p in poly.points:
            res += p.x + p.y
    b = time.time()
    print '  capnpy_struct:         %9.4f ms (res=%d)' % ((b-a)*1000, res)


def bench_string():
    print 'String benchmark:'
    plist = [PyPoint(1, 2, 'this is a point') for i in range(N)]
    res = 0
    a = time.time()
    for p in plist:
        if p.name == 'this is a point':
            res += 1
    b = time.time()
    print '  namedtuple:            %9.4f ms (res=%d)' % ((b-a)*1000, res)

    plist = [capnpy_struct.decode_message(point_bytes, capnpy_struct.Point)
             for i in range(N)]
    res = 0
    a = time.time()
    for p in plist:
        if p.name == 'this is a point':
            res += 1
    b = time.time()
    print '  capnpy_struct:         %9.4f ms (res=%d)' % ((b-a)*1000, res)


N = 100000

## bench_string()
## bench_string()
## bench_rect()
## bench_rect()
## bench_poly()
## bench_poly()
## sys.exit(0)


print '<first run>'
bench_point()
print
bench_rect()
print
bench_poly()
print
bench_string()
print
print
print '<second run>'
bench_point()
print
bench_rect()
print
bench_poly()
print
bench_string()
