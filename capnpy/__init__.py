import sys
import importlib.metadata

from capnpy.compiler.compiler import DynamicCompiler
from capnpy.compiler.distutils import capnpify
from capnpy.message import load, loads, load_all, dumps, dump
from capnpy.reflection import get_reflection_data


try:
    __version__ = importlib.metadata.version('capnpy')
except Exception:
    __version__ = 'unknown'

_compiler = DynamicCompiler(sys.path)
load_schema = _compiler.load_schema
parse_schema = _compiler.parse_schema
