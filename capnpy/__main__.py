from __future__ import print_function

import argparse
import sys
import time

from capnpy import load_schema
from capnpy.message import load
from capnpy.annotate import Options
from capnpy.compiler.compiler import StandaloneCompiler


def make_parser():
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument('--no-convert-case', action='store_true',
                        help="Don't convert camelCase to camel_case")
    parent.add_argument('--text-type', default='bytes',
                        choices=('bytes', 'unicode'),
                        help='Type to use to represent Text fields '
                             '(default: bytes)')
    parent.add_argument('--no-pyx', action='store_true',
                        help='Always produce a .py file, even if Cython '
                             'is available')
    parent.add_argument('--no-version-check', action='store_true',
                        help="Don't check for version discrepancy")
    parent.add_argument('--no-reflection', action='store_true',
                        help="Don't include reflection data in the "
                             "generated schema")

    parser = argparse.ArgumentParser(prog='capnpy')
    sub = parser.add_subparsers(dest='command')
    sub.required = True

    compile_p = sub.add_parser('compile', parents=[parent],
                               help='Compile a Cap\'n Proto schema')
    compile_p.add_argument('FILE', help='The .capnp file to compile')

    decode_p = sub.add_parser('decode', parents=[parent],
                              help='Decode a Cap\'n Proto binary stream')
    decode_p.add_argument('FILE', help='The binary file to decode')
    decode_p.add_argument('SCHEMA', help='The schema module name')
    decode_p.add_argument('CLASS', help='The class name to decode as')

    return parser


def parse_argv(argv):
    parser = make_parser()
    ns = parser.parse_args(argv)
    args = {
        'compile': ns.command == 'compile',
        'decode': ns.command == 'decode',
        'FILE': ns.FILE,
        'SCHEMA': getattr(ns, 'SCHEMA', None),
        'CLASS': getattr(ns, 'CLASS', None),
        '--pyx': False if ns.no_pyx else 'auto',
    }
    kwargs = dict(
        version_check=not ns.no_version_check,
        convert_case=not ns.no_convert_case,
        text_type=ns.text_type,
        include_reflection_data=not ns.no_reflection,
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
