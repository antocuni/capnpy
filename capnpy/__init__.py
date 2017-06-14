import sys
import pkg_resources
from capnpy.compiler.compiler import DynamicCompiler
from capnpy.compiler.distutils import capnpify
from capnpy.message import load, loads, load_all, dumps, dump

try:
    __version__ = pkg_resources.get_distribution('capnpy').version
except Exception:
    __version__ = 'unknown'

_compiler = DynamicCompiler(sys.path)
load_schema = _compiler.load_schema
parse_schema = _compiler.parse_schema
