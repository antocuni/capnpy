import sys
import time
from capnpy.message import load
from capnpy.compiler import load_schema

def main():
    cmd = sys.argv[1]
    assert cmd == 'decode'
    filename = sys.argv[2]
    schemaname = sys.argv[3]
    clsname = sys.argv[4]
    print >> sys.stderr, 'Loading schema...'
    a = time.time()
    mod = load_schema(schemaname, convert_case=False)
    b = time.time()
    print >> sys.stderr, 'schema loaded in %.2f secs' % (b-a)
    print >> sys.stderr, 'decoding stream...'
    cls = getattr(mod, clsname)
    with open(filename) as f:
        i = 0
        while True:
            try:
                obj = load(f, cls)
            except ValueError:
                break
            print obj.shortrepr()
            i += 1
            if i % 10000 == 0:
                print >> sys.stderr, i
    c = time.time()
    print >> sys.stderr, 'stream decoded in %.2f secs' % (c-b)

if __name__ == '__main__':
    main()
