import struct
from capnpy.ptr import StructPtr, ListPtr
from capnpy.blob import Blob, Types


class Struct(Blob):
    """
    Abstract base class: a blob representing a struct.

    subclasses of Struct needs to provide two attributes: __data_size__ and
    __ptrs_size__; there are two alternatives:

    1) you put the as class attributes in your subclass

    2) you use GenericStruct, where they are instance attributes (and thus
       less space-efficient, but it's handy if you need to walk the buffer
       without knowing the schema
    """

    __union_tag_offset__ = None
    __union_tag__ = None

    def which(self):
        """
        Return the value of the union tag, if the struct has an anonimous union or
        is an union
        """
        if self.__union_tag_offset__ is None:
            raise TypeError("Cannot call which() on a non-union type")
        val = self._read_primitive(self.__union_tag_offset__, Types.Int16)
        return self.__union_tag__(val)

    def _ensure_union(self, expected_tag):
        tag = self.which()
        if tag != expected_tag:
            raise ValueError("Tried to read an union field which is not currently "
                             "initialized. Expected %s, got %s" % (expected_tag, tag))


    def _ptr_offset_by_index(self, i):
        return (self.__data_size__ + i) * 8

    def _get_body_range(self):
        return self._get_body_start(), self._get_body_end()

    def _get_extra_range(self):
        return self._get_extra_start(), self._get_extra_end()

    def _get_body_start(self):
        return self._offset

    def _get_body_end(self):
        return self._offset + (self.__data_size__ + self.__ptrs_size__) * 8

    def _get_extra_start(self):
        if self.__ptrs_size__ == 0:
            return self._get_body_end()
        ptr_offset = self._ptr_offset_by_index(0)
        ptr = self._read_ptr(ptr_offset)
        return self._offset + ptr.deref(ptr_offset)

    def _get_extra_end(self):
        if self.__ptrs_size__ == 0:
            return self._get_body_end()
        #
        # the end of our extra correspond to the end of our last pointer: see
        # doc/normalize.rst for an explanation of why we can compute the extra
        # range this way
        ptr_offset = self._ptr_offset_by_index(self.__ptrs_size__ - 1)
        blob = self._follow_generic_pointer(ptr_offset)
        return blob._get_end()

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
        data_end = start + self.__data_size__*8
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
        ptrs_start = start + self.__data_size__*8
        ptrs_key = [''] * self.__ptrs_size__ # pre-allocate list
        offset = ptrs_start + 4
        for i in range(self.__ptrs_size__):
            ptrs_key[i] = struct.unpack_from('i', self._buf, offset)
            offset += 8
        return tuple(ptrs_key)

    def _get_extra_key(self):
        extra_start, extra_end = self._get_extra_range()
        return self._buf[extra_start:extra_end]

    def __eq__(self, other):
        if self.__class__ is not other.__class__:
            return False
        return self._get_key() == other._get_key()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self._get_key())

    def __lt__(self, other):
        raise TypeError, "capnpy structs can be compared only for equality"

    __le__ = __lt__
    __gt__ = __lt__
    __ge__ = __lt__


class GenericStruct(Struct):

    @classmethod
    def from_buffer_and_size(cls, buf, offset, data_size, ptrs_size):
        self = cls.from_buffer(buf, offset)
        self.__data_size__ = data_size
        self.__ptrs_size__ = ptrs_size
        return self
