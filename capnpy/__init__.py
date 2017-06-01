import sys
from capnpy.compiler.compiler import DynamicCompiler
from capnpy.compiler.distutils import capnpify
from capnpy.message import load, loads, load_all, dumps, dump

_compiler = DynamicCompiler(sys.path)
load_schema = _compiler.load_schema
parse_schema = _compiler.parse_schema
