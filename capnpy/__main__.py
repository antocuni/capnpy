"""
Usage: capnpy compile FILE [options]
       capnpy decode FILE SCHEMA CLASS [options]

Options:
  --no-convert-case    Don't convert camelCase to camel_case
  --no-pyx             Always produce a .py file, even if Cython is available
  --no-version-check   Don't check for version discrepancy.
"""
from __future__ import print_function

import sys
import time
import docopt

from capnpy import load_schema
from capnpy.message import load
from capnpy.compiler.compiler import StandaloneCompiler


def decode(args):
    print('Loading schema...', file=sys.stderr)
    a = time.time()
    mod = load_schema(modname=args['SCHEMA'],
                      convert_case=args['--convert-case'],
                      pyx=args['--pyx'])
    b = time.time()
    print('schema loaded in %.2f secs' % (b-a), file=sys.stderr)
    print('decoding stream...', file=sys.stderr)
    cls = getattr(mod, args['CLASS'])
    with open(args['FILE'], 'rb') as f:
        i = 0
        while True:
            try:
                obj = load(f, cls)
            except ValueError:
                break
            print(obj.shortrepr())
            i += 1
            if i % 10000 == 0:
                print(i, file=sys.stderr, end='\r')
    c = time.time()
    print('\nstream decoded in %.2f secs' % (c-b), file=sys.stderr)

def compile(args):
    comp = StandaloneCompiler(sys.path)
    comp.compile(filename=args['FILE'],
                 convert_case=args['--convert-case'],
                 pyx=args['--pyx'],
                 version_check=args['--version-check'])

def main(argv=None):
    args = docopt.docopt(__doc__, argv=argv)
    args['--convert-case'] = not args['--no-convert-case']
    args['--pyx'] = 'auto'
    if args['--no-pyx']:
        args['--pyx'] = False
    args['--version-check'] = not args['--no-version-check']
    if args['compile']:
        compile(args)
    elif args['decode']:
        decode(args)

if __name__ == '__main__':
    main()
