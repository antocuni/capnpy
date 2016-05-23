import sys
from capnpy.compiler.compiler import DynamicCompiler
from capnpy.compiler.distutils import capnpify
from capnpy.message import load, loads, dumps

_compiler = DynamicCompiler(sys.path, pyx='auto')
load_schema = _compiler.load_schema
