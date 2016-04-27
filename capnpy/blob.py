# glossary:
#
#   - size: they are always expressed in WORDS
#   - length: they are always expressed in BYTES


import struct
import capnpy
from capnpy.util import extend
from capnpy import ptr
from capnpy.type import Types
from capnpy.printer import BufferPrinter
from capnpy.unpack import unpack_primitive, unpack_int64, unpack_int16
from capnpy import _hash

try:
    import cython
except ImportError:
    PYX = False
else:
    PYX = cython.compiled


class CapnpBuffer(object):
    """
    Represent a capnproto buffer for a single-segment message. Far pointers are
    not allowed here
    """

    def __init__(self, s):
        self.s = s

    def read_primitive(self, offset, ifmt):
        return unpack_primitive(ifmt, self.s, offset)

    def read_int16(self, offset):
        return unpack_int16(self.s, offset)

    def read_raw_ptr(self, offset):
        return unpack_int64(self.s, offset)

    def read_ptr(self, offset):
        """
        Return the pointer at the specifield offet.

        WARNING: you MUST check if the return value is E_IS_FAR_POINTER, and
        in that case call read_far_ptr. We need this messy interface for
        speed; the proper alternative would be to simply return a tuple
        (offset, p) and handle the far ptr here: this is fine on PyPy but slow
        on CPython, because this way we cannot give a static return type.

        We could raise an exception instead of returning an error value:
        however, this is ~20% slower.
        """
        p = self.read_raw_ptr(offset)
        if ptr.kind(p) == ptr.FAR:
            return ptr.E_IS_FAR_POINTER
        return p

    def read_far_ptr(self, offset):
        raise ValueError("Cannot read a far pointer inside a single-segment message")

    def read_str(self, p, offset, default_, additional_size):
        """
        Read Text or Data from the pointer ``p``, which was read from the given
        offset.

        If you want to read a Text, pass additional_size=-1 to remove the
        trailing '\0'. If you want to read a Data, pass additional_size=0.
        """
        if p == 0:
            return default_
        assert ptr.kind(p) == ptr.LIST
        assert ptr.list_size_tag(p) == ptr.LIST_SIZE_8
        start = ptr.deref(p, offset)
        end = start + ptr.list_item_count(p) + additional_size
        return self.s[start:end]

    def hash_str(self, p, offset, default_, additional_size):
        if p == 0:
            return default_
        assert ptr.kind(p) == ptr.LIST
        assert ptr.list_size_tag(p) == ptr.LIST_SIZE_8
        start = ptr.deref(p, offset)
        size = ptr.list_item_count(p) + additional_size
        return _hash.strhash(self.s, start, size)


class CapnpBufferWithSegments(CapnpBuffer):
    """
    Represent a capnproto buffer for a multiple segments message. The segments
    are stored in a single consecutive area of memory, and segment_offsets
    stores the offset at which each segment starts.
    """

    def __init__(self, s, segment_offsets):
        assert segment_offsets is not None
        self.s = s
        self.segment_offsets = segment_offsets

    def read_far_ptr(self, offset):
        """
        Read and return the ptr referenced by this far pointer
        """
        p = self.read_raw_ptr(offset)
        assert ptr.far_landing_pad(p) == 0
        segment_start = self.segment_offsets[ptr.far_target(p)] # in bytes
        offset  = segment_start + ptr.far_offset(p)*8
        p = self.read_raw_ptr(offset)
        return offset, p


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

    def _init_blob(self, buf):
        if isinstance(buf, str):
            buf = CapnpBuffer(buf)
        self._buf = buf

    def _read_ptr_generic(self, offset):
        """
        Abstract method to read a pointer at the specified offset. Implemented
        differently by Struct and List, it is used only to do a generic
        traversal of a message. It returns a tuple (offset, p).

        Not to be confused with Struct._read_fast_ptr, which is the "real"
        logic to read a statically-typed field, and returns only a p (for
        performance).
        """
        raise NotImplementedError

    def _read_list_or_struct(self, ptr_offset, default_=None):
        ptr_offset, p = self._read_ptr_generic(ptr_offset)
        if p == 0:
            return default_
        blob_offet = ptr.deref(p, ptr_offset)
        if ptr.kind(p) == ptr.STRUCT:
            Struct = capnpy.struct_.Struct
            return Struct.from_buffer(self._buf,
                                      blob_offet,
                                      ptr.struct_data_size(p), ptr.struct_ptrs_size(p))
        elif ptr.kind(p) == ptr.LIST:
            List = capnpy.list.List
            return List.from_buffer(self._buf,
                                    blob_offet,
                                    ptr.list_size_tag(p), ptr.list_item_count(p), Blob)
        else:
            assert False, 'Unkwown pointer kind: %s' % ptr.kind(p)

    def _print_buf(self, start=None, end='auto', **kwds):
        if start is None:
            start = self._data_offset
        if end == 'auto':
            end = self._get_body_end()
        elif end is None:
            end = len(self._buf.s)
        p = BufferPrinter(self._buf.s)
        p.printbuf(start=start, end=end, **kwds)


# that these two modules are used by _read_list_or_struct. We need to put them
# at the end because of circular references
import capnpy.struct_
import capnpy.list
