import struct
from capnpy.ptr import Ptr, StructPtr, ListPtr, FarPtr
from capnpy.blob import Blob, Types

undefined = object()

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

    def __init__(self, buf, offset, segment_offsets, data_size, ptrs_size):
        Blob.__init__(self, buf, offset, segment_offsets)
        self._data_size = data_size
        self._ptrs_size = ptrs_size

    @classmethod
    def from_buffer(cls, buf, offset, segment_offsets, data_size, ptrs_size):
        self = cls.__new__(cls)
        Struct.__init__(self, buf, offset, segment_offsets, data_size, ptrs_size)
        return self

    def which(self):
        """
        Return the value of the union tag, if the struct has an anonimous union or
        is an union
        """
        if self.__tag_offset__ is None:
            raise TypeError("Cannot call which() on a non-union type")
        val = self._read_data(self.__tag_offset__, Types.int16)
        return self.__tag__(val)

    def _read_data(self, offset, t):
        if offset >= self._data_size*8:
            # reading bytes beyond _data_size is equivalent to read 0
            return 0
        return self._read_primitive(offset, t)

    def _read_bit(self, offset, bitmask):
        val = self._read_data(offset, Types.uint8)
        return bool(val & bitmask)

    def _read_enum(self, offset, enumtype):
        val = self._read_data(offset, Types.int16)
        return enumtype(val)

    def _read_struct(self, offset, structcls):
        """
        Read and dereference a struct pointer at the given offset.  It returns an
        instance of ``cls`` pointing to the dereferenced struct.
        """
        offset, ptr = self._read_ptr(offset)
        if ptr is None:
            return None
        assert ptr.kind == StructPtr.KIND
        ptr = ptr.specialize()
        struct_offset = ptr.deref(offset)
        return structcls.from_buffer(self._buf,
                                     self._offset+struct_offset,
                                     self._segment_offsets,
                                     ptr.data_size,
                                     ptr.ptrs_size)

    @classmethod
    def _assert_undefined(cls, val, name, other_name):
        if val is not undefined:
            raise TypeError("got multiple values for the union tag: %s, %s" %
                            (name, other_name))

    def _ensure_union(self, expected_tag):
        tag = self.which()
        if tag != expected_tag:
            raise ValueError("Tried to read an union field which is not currently "
                             "initialized. Expected %s, got %s" % (expected_tag, tag))


    def _ptr_offset_by_index(self, i):
        return (self._data_size + i) * 8

    def _get_body_range(self):
        return self._get_body_start(), self._get_body_end()

    def _get_extra_range(self):
        return self._get_extra_start(), self._get_extra_end()

    def _get_body_start(self):
        return self._offset

    def _get_body_end(self):
        return self._offset + (self._data_size + self._ptrs_size) * 8

    def _get_extra_start(self):
        if self._ptrs_size == 0:
            return self._get_body_end()
        for i in range(self._ptrs_size):
            ptr_offset = self._ptr_offset_by_index(i)
            ptr = self._read_raw_ptr(ptr_offset)
            assert ptr.kind != FarPtr.KIND
            if ptr != 0:
                return self._offset + ptr.deref(ptr_offset)
        #
        # if we are here, it means that all ptrs are null
        return self._get_body_end()

    def _get_extra_end_maybe(self):
        if self._ptrs_size == 0:
            return None # no extra
        #
        # the end of our extra correspond to the end of our last non-null
        # pointer: see doc/normalize.rst for an explanation of why we can
        # compute the extra range this way
        #
        # XXX: we should probably unroll this loop
        i = self._ptrs_size - 1 # start from the last ptr
        while i >= 0:
            ptr_offset = self._ptr_offset_by_index(i)
            blob = self._read_generic_pointer(ptr_offset)
            if blob is not None:
                return blob._get_end()
            i -= 1
        #
        # if we are here, it means that ALL ptrs are NULL, so we don't have
        # any extra section
        return None

    def _get_extra_end(self):
        end = self._get_extra_end_maybe()
        if end is None:
            return self._get_body_end()
        return end

    def _get_end(self):
        return self._get_extra_end()

    def _get_key(self):
        """
        The _key is used to implement __eq__, __ne__ and __hash__.
        It's a 3-tuple:

          - the data section (copied verbatim)

          - the non-offset part of the ptrs section

          - the extra section (copied verbatim)
        """
        return self._get_data_key(), self._get_ptrs_key(), self._get_extra_key()

    def _get_data_key(self):
        start = self._get_body_start()
        data_end = start + self._data_size*8
        return self._buf[start:data_end]

    def _get_ptrs_key(self):
        """
        Return a tuple containing the 16 most significant bits of each ptr.

        In other words, we explicitly ignore the "offset" part of each ptr,
        becuase it might differ even if the structs are equal: in particular,
        if the struct has a "garbage" section, the offsets in the ptrs change.
        See doc/normalize.rst for a more detailed explanation.

        The most significant 16 bits of each ptr are read using
        struct.unpack_from: in microbenchmarks, this has been measured to be
        ~5x faster than taking string slices, on PyPy.

        NOTE: this is a general implementation which works for every struct,
        but it's not the fastest possible. Subclasses are expected to override
        this this method, like this::

            return (struct.unpack_from('i', self._buf,  4),
                    struct.unpack_from('i', self._buf, 12),
                    ...)
        """
        start = self._get_body_start()
        ptrs_start = start + self._data_size*8
        ptrs_key = [''] * self._ptrs_size # pre-allocate list
        offset = ptrs_start + 4
        for i in range(self._ptrs_size):
            ptrs_key[i] = struct.unpack_from('i', self._buf, offset)
            offset += 8
        return tuple(ptrs_key)

    def _get_extra_key(self):
        extra_start, extra_end = self._get_extra_range()
        return self._buf[extra_start:extra_end]

    def _split(self, extra_offset):
        """
        Split the body and the extra part.  The extra part must be placed at the
        specified offset, in words. The ptrs in the body will be adjusted
        accordingly.
        """
        if self._ptrs_size == 0:
            # easy case, just copy the body
            start, end = self._get_body_range()
            return self._buf[start:end], ''
        #
        # hard case. The layout of self._buf is like this:
        # +----------+------+------+----------+-------------+
        # | garbage0 | data | ptrs | garbage1 |    extra    |
        # +----------+------+------+----------+-------------+
        #                    |   |             ^     ^
        #                    +-----------------+     |
        #                        |                   |
        #                        +-------------------+
        #
        # We recompute the pointers assumining len(garbage1) == extra_offset
        #
        # 1) the data section is copied verbatim
        # 2) the offset of pointers in ptrs are adjusted
        # 3) extra is copied verbatim
        #
        body_start, body_end = self._get_body_range()
        extra_start, extra_end = self._get_extra_range()
        #
        # 1) data section
        data_size = self._data_size
        data_buf = self._buf[body_start:body_start+data_size*8]
        #
        # 2) ptrs section
        #    for each ptr:
        #        ptr.offset += (extra_offset - old_extra_offset)/8
        #
        # NOTE: ptr.offset is in words, extra_start and body_end in bytes
        old_extra_offset = (extra_start - body_end)/8
        additional_offset = extra_offset - old_extra_offset
        #
        # iterate over and fix the pointers
        parts = [data_buf]
        for j in range(self._ptrs_size):
            # read pointer, update its offset, and pack it
            ptr = self._read_raw_ptr(self._ptr_offset_by_index(j))
            if ptr != 0:
                assert ptr.kind != FarPtr.KIND
                ptr = Ptr.new(ptr.kind, ptr.offset+additional_offset, ptr.extra)
            s = struct.pack('q', ptr)
            parts.append(s)
        #
        body_buf = ''.join(parts)
        # 3) extra part
        extra_buf = self._buf[extra_start:extra_end]
        #
        return body_buf, extra_buf

    def compact(self):
        """
        Return a compact version of the object, removing the garbage around the
        body and the extra parts.
        """
        body, extra = self._split(0)
        buf = body+extra
        return self.__class__.from_buffer(buf, 0, None,
                                          self._data_size, self._ptrs_size)

    def __hash__(self):
        return hash(self._get_key())

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
    #   1. we write the actual logic inside the _cmp_* methods
    #
    #   2. we implement a __richcmp__ which will be used by Cython but ignored
    #      by Pure Python
    #
    #   3. we add __eq__, __lt__, etc. OUTSIDE the class definition. The
    #      assignments will fail when Struct is compiled by Cython, because
    #      you cannot modify the class dict of an extension type: this means
    #      that we will have the special methods only when in Pure Python
    #      mode, as wished

    def _cmp_eq(self, other):
        if self.__class__ is not other.__class__:
            return False
        return self._get_key() == other._get_key()

    def _cmp_ne(self, other):
        return not self._cmp_eq(other)

    def _cmp_error(self, other):
        raise TypeError, "capnpy structs can be compared only for equality"

    def __richcmp__(self, other, op):
        if op == 2:
            return self._cmp_eq(other)
        elif op == 3:
            return self._cmp_ne(other)
        else:
            return self._cmp_error(other)


# add the special methods only when Struct has NOT been compiled by
# Cython. See the comment above for more explanation
try:
    Struct.__eq__ = Struct.__dict__['_cmp_eq']
    Struct.__ne__ = Struct.__dict__['_cmp_ne']
    Struct.__lt__ = Struct.__dict__['_cmp_error']
    Struct.__le__ = Struct.__dict__['_cmp_error']
    Struct.__gt__ = Struct.__dict__['_cmp_error']
    Struct.__ge__ = Struct.__dict__['_cmp_error']
except TypeError:
    pass
