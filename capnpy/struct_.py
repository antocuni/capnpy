import capnpy
from capnpy import ptr
from capnpy.type import Types
from capnpy.blob import Blob
from capnpy.visit import end_of
from capnpy.list import List
from capnpy.packing import pack_int64
from capnpy.segment.builder import SegmentBuilder
from capnpy.util import magic_setattr

class Undefined(object):
    def __repr__(self):
        return '<undefined>'
undefined = Undefined()

def check_tag(curtag, newtag):
    if curtag is not None:
        raise TypeError("got multiple values for the union tag: %s, %s" %
                        (curtag, newtag))
    return newtag


def struct_from_buffer(cls, buf, offset, data_size, ptrs_size):
    """
    Same as cls.from_buffer, but since Cython does not support classmethod,
    at least this can be called from C
    """
    self = cls.__new__(cls)
    self._init_from_buffer(buf, offset, data_size, ptrs_size)
    return self

class Struct(Blob):
    """
    Abstract base class: a blob representing a struct.
    """

    __tag_offset__ = None
    __tag__ = None

    # __static_{data,ptrs}_size__ contain the size of the struct as known from
    # the schema: they are class attributes. On the other hand, _data_size and
    # _ptrs_size contain the size as specified by the pointer which is
    # pointing to the particular capnp struct, so they are instance attributes
    __static_data_size__ = None
    __static_ptrs_size__ = None

    def __init__(self, buf, offset, data_size, ptrs_size):
        self._init_from_buffer(buf, offset, data_size, ptrs_size)

    def _init_from_buffer(self, buf, offset, data_size, ptrs_size):
        self._init_blob(buf)
        self._data_offset = offset
        self._ptrs_offset = offset + data_size*8
        self._data_size = data_size
        self._ptrs_size = ptrs_size
        assert self._data_offset + data_size*8 <= len(self._seg.buf)
        assert self._ptrs_offset + ptrs_size*8 <= len(self._seg.buf)

    def _init_from_pointer(self, buf, offset, p):
        assert ptr.kind(p) == ptr.STRUCT
        struct_offset = ptr.deref(p, offset)
        data_size = ptr.struct_data_size(p)
        ptrs_size = ptr.struct_ptrs_size(p)
        self._init_from_buffer(buf, struct_offset, data_size, ptrs_size)

    def __reduce__(self):
        # pickle support
        args = (self.__class__, self._seg, self._data_offset,
                self._data_size, self._ptrs_size)
        return (struct_from_buffer, args)

    @classmethod
    def from_buffer(cls, buf, offset, data_size, ptrs_size):
        return struct_from_buffer(cls, buf, offset, data_size, ptrs_size)

    @classmethod
    def load(cls, f):
        return capnpy.message.load(f, cls)

    @classmethod
    def loads(cls, s):
        return capnpy.message.loads(s, cls)

    @classmethod
    def load_all(cls, f):
        return capnpy.message.load_all(f, cls)

    def shortrepr(self):
        return '(no shortrepr)'

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.shortrepr())

    def which(self):
        """
        Return the value of the union tag, if the struct has an anonimous union or
        is an union.
        """
        return self.__tag__(self.__which__())

    def __which__(self):
        if self.__tag_offset__ is None:
            raise TypeError("Cannot call which() on a non-union type")
        return self._read_data_int16(self.__tag_offset__)

    def _as_pointer(self, offset):
        """
        Return a pointer p which points to this structure, assuming that p will be
        read at ``offset``
        """
        p_offset = (self._data_offset - offset - 8) / 8
        return ptr.new_struct(p_offset, self._data_size, self._ptrs_size)

    def _read_fast_ptr(self, offset):
        # Struct-specific logic
        if offset >= self._ptrs_size*8:
            return 0
        return self._seg.read_ptr(self._ptrs_offset+offset)

    def _read_far_ptr(self, offset):
        if offset >= self._ptrs_size*8:
            return offset, 0
        return self._seg.read_far_ptr(self._ptrs_offset+offset)

    def _read_data(self, offset, ifmt):
        if offset >= self._data_size*8:
            # reading bytes beyond _data_size is equivalent to read 0
            return 0
        return self._seg.read_primitive(self._data_offset+offset, ifmt)

    def _read_data_int16(self, offset):
        if offset >= self._data_size*8:
            # reading bytes beyond _data_size is equivalent to read 0
            return 0
        return self._seg.read_int16(self._data_offset+offset)

    def _read_bit(self, offset, bitmask):
        val = self._read_data(offset, Types.uint8.ifmt)
        return bool(val & bitmask)

    def _read_struct(self, offset, structcls):
        """
        Read and dereference a struct pointer at the given offset.  It returns an
        instance of ``structcls`` pointing to the dereferenced struct.
        """
        p = self._read_fast_ptr(offset)
        if ptr.kind(p) == ptr.FAR:
            offset, p = self._read_far_ptr(offset)
        else:
            offset += self._ptrs_offset
        if p == 0:
            return None
        assert ptr.kind(p) == ptr.STRUCT
        obj = structcls.__new__(structcls)
        obj._init_from_pointer(self._seg, offset, p)
        return obj

    def _read_list(self, offset, item_type, default_=None):
        p = self._read_fast_ptr(offset)
        if ptr.kind(p) == ptr.FAR:
            offset, p = self._read_far_ptr(offset)
        else:
            offset += self._ptrs_offset
        if p == 0:
            return default_
        assert ptr.kind(p) == ptr.LIST
        list_offset = ptr.deref(p, offset)
        # in theory we could simply use List.from_buffer; however, Cython is
        # not able to compile classmethods, so we create it manually
        obj = List.__new__(List)
        obj._init_from_buffer(self._seg,
                              list_offset,
                              ptr.list_size_tag(p),
                              ptr.list_item_count(p),
                              item_type)
        return obj

    def _read_str_text(self, offset, default_=None):
        return self._read_str_data(offset, default_, additional_size=-1)

    def _hash_str_text(self, offset, default_=hash(None)):
        return self._hash_str_data(offset, default_, additional_size=-1)

    def _read_str_data(self, offset, default_=None, additional_size=0):
        p = self._read_fast_ptr(offset)
        if ptr.kind(p) == ptr.FAR:
            offset, p = self._read_far_ptr(offset)
        else:
            offset += self._ptrs_offset
        return self._seg.read_str(p, offset, default_, additional_size)

    def _hash_str_data(self, offset, default_=hash(None), additional_size=0):
        p = self._read_fast_ptr(offset)
        if ptr.kind(p) == ptr.FAR:
            offset, p = self._read_far_ptr(offset)
        else:
            offset += self._ptrs_offset
        return self._seg.hash_str(p, offset, default_, additional_size)

    def _ensure_union(self, expected_tag):
        if self.__which__() != expected_tag:
            tag = self.which() # use the non-raw tag to get a better error message
            raise ValueError("Tried to read an union field which is not currently "
                             "initialized. Expected %s, got %s" % (expected_tag, tag))


    def _get_end(self):
        p = ptr.new_struct(0, self._data_size, self._ptrs_size)
        return end_of(self._seg, p, self._data_offset-8)

    def _is_compact(self):
        return self._get_end() != -1

    def compact(self):
        """
        Return a compact version of the struct. In case the struct was inside a
        bigger message, it "extracts" it into a new message which contains
        only the needed pieces.
        """
        builder = SegmentBuilder()
        pos = builder.allocate(8)
        builder.copy_from_struct(pos, Struct, self)
        buf = builder.as_string()
        t = type(self)
        res = t.__new__(t)
        res._init_from_buffer(buf, 8, self._data_size, self._ptrs_size)
        return res

    # ----------------------
    # hashing and equality
    # ----------------------

    # in theory, this is the only method you nedd to override to enable
    # hashing and comparability. But in PYX mode, we override _hash and
    # _equals as well.
    def _key(self):
        raise TypeError("Cannot hash or compare capnpy structs. "
                        "Use the $Py.key annotation to enable it")

    def __hash__(self):
        return hash(self._key())

    def _equals(self, other):
        mykey = self._key()
        if isinstance(other, tuple):
            otherkey = other
        else:
            otherkey = other._key()
        return mykey == otherkey

    # this is already defined in blob.py: however, it seems if we do not
    # redeclare it here, Cython won't use it
    def __richcmp__(self, other, op):
        return self._richcmp(other, op)


# Attach the dump[s] methods to Struct. This is the only way I found to make
# sure that Struct.dumps is implemented in C (on CPython). The obvious
# alternative is to implement dumps directly in the class body and to declare
# it as cpdef in struct_.pxd: however, this cannot work because there are
# circular dependencies between struct_.pxd and message.pxd. This gives a ~20%
# improvement.
import capnpy.message
magic_setattr(Struct, 'dump', capnpy.message.dump)
magic_setattr(Struct, 'dumps', capnpy.message.dumps)
