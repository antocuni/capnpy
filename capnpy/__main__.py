"""
Usage: capnpy compile FILE [options]
       capnpy decode FILE SCHEMA CLASS [options]

Options:
  --no-convert-case    Don't convert camelCase to camel_case
  --text-type=TYPE     Type to use to represent Text fields [Default: bytes]
                       Can be bytes or unicode
  --no-pyx             Always produce a .py file, even if Cython is available
  --no-version-check   Don't check for version discrepancy
  --no-reflection      Don't include reflection data in the generated schema
"""
from __future__ import print_function

import sys
import time
import docopt

from capnpy import load_schema
from capnpy.message import load
from capnpy.annotate import Options
from capnpy.compiler.compiler import StandaloneCompiler

def parse_argv(argv):
    args = docopt.docopt(__doc__, argv=argv)
    if args['--text-type'] not in ('bytes', 'unicode'):
        print(__doc__)
        print()
        print('ERROR: --text-type can be only bytes or unicode')
        raise SystemExit(1)
    #
    args['--pyx'] = 'auto'
    if args['--no-pyx']:
        args['--pyx'] = False
    del args['--no-pyx']
    #
    kwargs = dict(
        version_check = not args['--no-version-check'],
        convert_case = not args['--no-convert-case'],
        text_type = args['--text-type'],
        include_reflection_data = not args['--no-reflection'],
    )
    return args, Options.from_dict(kwargs)

def decode(args, options):
    print('Loading schema...', file=sys.stderr)
    a = time.time()
    mod = load_schema(modname=args['SCHEMA'],
                      pyx=args['--pyx'],
                      options=options)
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

def compile(args, options):
    comp = StandaloneCompiler(sys.path)
    comp.compile(filename=args['FILE'],
                 pyx=args['--pyx'],
                 options=options)


def main(argv=None):
    args, options = parse_argv(argv)
    if args['compile']:
        compile(args, options)
    elif args['decode']:
        decode(args, options)

if __name__ == '__main__':
    sys.exit(main())
