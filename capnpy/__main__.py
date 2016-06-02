"""
Usage: capnpy compile FILE [options]
       capnpy decode FILE SCHEMA CLASS [options]

Options:
  --no-convert-case    Don't convert camelCase to camel_case
  --no-pyx             Always produce a .py file, even if Cython is available
"""

import sys
import py
import time
import docopt
from capnpy import load_schema
from capnpy.message import load
from capnpy.compiler.compiler import StandaloneCompiler


def decode(args):
    print >> sys.stderr, 'Loading schema...'
    a = time.time()
    mod = load_schema(args['SCHEMA'],
                      convert_case=args['--convert-case'],
                      pyx=args['--pyx'])
    b = time.time()
    print >> sys.stderr, 'schema loaded in %.2f secs' % (b-a)
    print >> sys.stderr, 'decoding stream...'
    cls = getattr(mod, args['CLASS'])
    with open(args['FILE']) as f:
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

def compile(args):
    srcfile = args['FILE']
    comp = StandaloneCompiler(sys.path)
    comp.compile(args['FILE'],
                 convert_case=args['--convert-case'],
                 pyx=args['--pyx'])

def main(argv=None):
    args = docopt.docopt(__doc__, argv=argv)
    args['--convert-case'] = not args['--no-convert-case']
    args['--pyx'] = 'auto'
    if args['--no-pyx']:
        args['--pyx'] = False
    if args['compile']:
        compile(args)
    elif args['decode']:
        decode(args)

if __name__ == '__main__':
    main()
