# glossary:
#
#   - size: they are always expressed in WORDS
#   - length: they are always expressed in BYTES

import sys
from pypytools import IS_PYPY
import capnpy
from capnpy.util import extend
from capnpy.printer import BufferPrinter
from capnpy.segment.segment import Segment

try:
    import cython
except ImportError:
    PYX = False
else:
    PYX = cython.compiled

if not IS_PYPY and not PYX:
    print >> sys.stderr, 'WARNING: capnpy was not compiled correctly, PYX mode disabled'


class Blob(object):
    """
    Abstract base class to read a generic capnp object.

    It contains very little logic: mostly, the methods on Blob are used only
    to do a generic traversal of a message, when you don't know the schema.
    """

    @classmethod
    def __extend__(cls, newcls):
        return extend(cls)(newcls)

    def __init__(self, buf):
        self._init_blob(buf)

    def _init_blob(self, seg):
        assert seg is not None
        if isinstance(seg, str):
            seg = Segment(seg)
        self._seg = seg

    def _print_buf(self, start=None, end='auto', **kwds):
        if start is None:
            start = self._data_offset
        if end == 'auto':
            end = self._get_end()
        elif end is None:
            end = len(self._seg.buf)
        p = BufferPrinter(self._seg.buf)
        p.printbuf(start=start, end=end, **kwds)


    # ------------------------------------------------------
    # Comparisons methods
    # ------------------------------------------------------
    #
    # this class can be used in two ways:
    #
    #   1. Pure Python mode (either on CPython or PyPy)
    #   2. compiled by Cython
    #
    # Cython does not support __eq__, __lt__ etc: instead, to enable
    # comparisons you need to define __richcmp__ (which Cython maps to the
    # CPython's tp_richcmp slot).  On the other hand, when in Pure Python
    # mode, we *need* __eq__, __lt__ etc:
    #
    #   1. we write the actual logic inside _cmp_*
    #
    #   2. we implement a __richcmp__ which will be used by Cython but ignored
    #      by Pure Python
    #
    #   3. we add __eq__, __lt__, etc. OUTSIDE the class definition. The
    #      assignments will fail when Struct is compiled by Cython, because
    #      you cannot modify the class dict of an extension type: this means
    #      that we will have the special methods only when in Pure Python
    #      mode, as wished

    def _equals(self, other):
        raise NotImplementedError

    def _cmp_eq(self, other):
        return self._equals(other)

    def _cmp_ne(self, other):
        return not self._equals(other)

    def _cmp_error(self, other):
        raise TypeError, "capnpy structs can be compared only for equality"

    def _richcmp(self, other, op):
        if op == 2:
            return self._cmp_eq(other)
        elif op == 3:
            return self._cmp_ne(other)
        else:
            return self._cmp_error(other)

    def __richcmp__(self, other, op):
        return self._richcmp(other, op)

# add the special methods only when Struct has NOT been compiled by
# Cython. See the comment above for more explanation
try:
    Blob.__eq__ = Blob.__dict__['_cmp_eq']
    Blob.__ne__ = Blob.__dict__['_cmp_ne']
    Blob.__lt__ = Blob.__dict__['_cmp_error']
    Blob.__le__ = Blob.__dict__['_cmp_error']
    Blob.__gt__ = Blob.__dict__['_cmp_error']
    Blob.__ge__ = Blob.__dict__['_cmp_error']
except TypeError:
    pass
