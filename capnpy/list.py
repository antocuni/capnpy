import struct
import capnpy
from capnpy.blob import Blob, Types, PYX
from capnpy import ptr
from capnpy.util import text_repr, float32_repr, float64_repr
from capnpy.visit import end_of
from capnpy.packing import pack_int64

class List(Blob):

    @classmethod
    def from_buffer(cls, buf, offset, size_tag, item_count, item_type):
        """
        buf, offset: the underlying buffer and the offset where the list starts

        item_length: the length of each list item, in BYTES. Note: this is NOT the
        value of the ListPtr.SIZE_* tag, although it's obviously based on it

        item_type: an instance of a subclass of ItemType
        """
        self = cls.__new__(cls)
        self._init_from_buffer(buf, offset, size_tag, item_count, item_type)
        return self

    def _init_from_buffer(self, buf, offset, size_tag, item_count, item_type):
        self._init_blob(buf)
        self._offset = offset
        self._item_type = item_type
        self._set_list_tag(size_tag, item_count)

    def __reduce__(self):
        raise TypeError("Cannot pickle capnpy List directly. Either pickle "
                        "the outer structure containing it, or convert it "
                        "to a Python list before pickling")

    def _set_list_tag(self, size_tag, item_count):
        self._size_tag = size_tag
        if size_tag == ptr.LIST_SIZE_COMPOSITE:
            tag = self._buf.read_raw_ptr(self._offset)
            self._tag = tag
            self._item_count = ptr.offset(tag)
            self._item_length = (ptr.struct_data_size(tag)+ptr.struct_ptrs_size(tag))*8
            self._item_offset = 8
        else:
            self._tag = -1
            self._item_count = item_count
            self._item_length = ptr.list_item_length(size_tag)
            self._item_offset = 0

    def __repr__(self):
        return '<capnpy list [%d items]>' % (len(self),)

    def __len__(self):
        return self._item_count

    def __getitem__(self, i):
        if isinstance(i, slice):
            idx = xrange(*i.indices(len(self)))
            return [self._getitem_fast(j) for j in idx]
        if i < 0:
            i += self._item_count
        if 0 <= i < self._item_count:
            return self._getitem_fast(i)
        raise IndexError

    def _getitem_fast(self, i):
        """
        WARNING: no bound checks!
        """
        return self._item_type.read_item(self, i)

    def _get_end(self):
        p = ptr.new_list(0, self._size_tag, self._item_count)
        return end_of(self._buf, p, self._offset-8)

    def _get_slice(self):
        # XXX: investigate whether it is faster to user memoryview for
        # comparing the memory without doing a full copy
        start = self._offset
        end = self._get_end()
        return self._buf.s[start:end]

    def _equals(self, other):
        if not self._item_type.can_compare():
            raise TypeError("Cannot compare lists of structs.")
        if isinstance(other, list):
            return list(self) == other
        if self.__class__ is not other.__class__:
            return False
        return (self._item_count == other._item_count and
                self._item_type.get_type() == other._item_type.get_type() and
                self._get_slice() == other._get_slice())

    def shortrepr(self):
        parts = [self._item_type.item_repr(item) for item in self]
        return '[%s]' % (', '.join(parts))


class ItemType(object):

    def get_type(self):
        raise NotImplementedError

    def offset_for_item(self, lst, i):
        return lst._item_offset + (i * lst._item_length)

    def read_item(self, lst, i):
        raise NotImplementedError

    def item_repr(self, item):
        raise NotImplementedError

    def can_compare(self):
        return True

    def get_item_length(self):
        raise NotImplementedError

    def pack_item(self, listbuilder, i, item):
        raise NotImplementedError


class VoidItemType(ItemType):

    def get_type(self):
        return Types.Void

    def offset_for_item(self, lst, i):
        return 0

    def read_item(self, lst, i):
        return None

    def item_repr(self, item):
        return 'void'

    def get_item_length(self):
        return 0, ptr.LIST_SIZE_VOID

    def pack_item(self, listbuilder, i, item):
        return ''


class BoolItemType(ItemType):

    def get_type(self):
        return Types.Bool

    def offset_for_item(self, lst, i):
        raise NotImplementedError

    def read_item(self, lst, i):
        byteoffset, bitoffset = divmod(i, 8)
        bitmask = 1 << bitoffset
        value = lst._buf.read_primitive(lst._offset+byteoffset, ord('b'))
        return bool(value & bitmask)

    def item_repr(self, item):
        return ('false', 'true')[item]

    def get_item_length(self):
        raise NotImplementedError

    def pack_item(self, listbuilder, i, item):
        raise NotImplementedError


class PrimitiveItemType(ItemType):

    def __init__(self, t):
        self.t = t
        self.ifmt = t.ifmt

    def get_type(self):
        return self.t

    def read_item(self, lst, i):
        offset = lst._offset + (i * lst._item_length)
        return lst._buf.read_primitive(offset, self.ifmt)

    def item_repr(self, item):
        if self.t is Types.float32:
            return float32_repr(item)
        elif self.t is Types.float64:
            return float64_repr(item)
        else:
            return repr(item)

    def get_item_length(self):
        length = self.t.calcsize()
        if length == 1:
            return length, ptr.LIST_SIZE_8
        elif length == 2:
            return length, ptr.LIST_SIZE_16
        elif length == 4:
            return length, ptr.LIST_SIZE_32
        elif length == 8:
            return length, ptr.LIST_SIZE_64
        else:
            raise ValueError('Unsupported size: %d' % length)

    def pack_item(self, listbuilder, i, item):
        return struct.pack('<'+self.t.fmt, item)


class EnumItemType(PrimitiveItemType):

    def __init__(self, enumcls):
        PrimitiveItemType.__init__(self, Types.int16)
        self.enumcls = enumcls

    def get_type(self):
        return self.enumcls

    def read_item(self, lst, i):
        value = PrimitiveItemType.read_item(self, lst, i)
        return self.enumcls(value)


class StructItemType(ItemType):

    def __init__(self, structcls):
        self.structcls = structcls
        self.static_data_size = structcls.__static_data_size__
        self.static_ptrs_size = structcls.__static_ptrs_size__

    def get_type(self):
        return self.structcls

    def can_compare(self):
        return False

    def read_item(self, lst, i):
        offset = self.offset_for_item(lst, i)
        return self.structcls.from_buffer(lst._buf,
                                          lst._offset+offset,
                                          ptr.struct_data_size(lst._tag),
                                          ptr.struct_ptrs_size(lst._tag))

    def item_repr(self, item):
        return item.shortrepr()

    def get_item_length(self):
        total_length = (self.static_data_size+self.static_ptrs_size)*8   # in bytes
        if total_length > 8:
            return total_length, ptr.LIST_SIZE_COMPOSITE
        assert False, 'XXX'

    def pack_item(self, listbuilder, i, item):
        structcls = self.structcls
        if not isinstance(item, structcls):
            raise TypeError("Expected an object of type %s, got %s instead" %
                            (self.structcls.__name__, item.__class__.__name__))
        #
        # This is the layout of the list:
        #
        # +-------+-------+...+-------+--------+--------+...+--------+
        # | body0 | body1 |   | bodyN | extra0 | extra1 |   | extraN |
        # +-------+-------+...+-------+--------+--------+...+--------+
        # |               |                    |
        # |- body_offset -|                    |
        # |               |--- extra_offset ---|
        # |                                    |
        # +------- _total_length --------------+
        #
        # When i==1, self._total_length will contain the offset up to the end
        # of extra0; extra1...extraN are not yet considered.
        #
        # The item body and extra are split by Struct._split, passing the
        # correct extra_offset.
        #
        # Note that extra_offset is expressed in WORDS, while _total_length in
        # BYTES
        struct_item = item
        body_offset = (self.static_data_size+self.static_ptrs_size) * (i+1)
        extra_offset = listbuilder._total_length/8 - body_offset
        body, extra = struct_item._split(extra_offset)
        listbuilder._alloc(extra)
        return body


class TextItemType(ItemType):

    def __init__(self, t):
        assert t in (Types.text, Types.data)
        self.additional_size = 0
        if t == Types.text:
            self.additional_size = -1

    def get_type(self):
        return self.t

    def read_item(self, lst, i):
        offset = lst._offset + (i*8)
        p = lst._buf.read_ptr(offset)
        if ptr.kind(p) == ptr.FAR:
            raise NotImplementedError('FAR pointers not supported here')
        return lst._buf.read_str(p, offset, None, self.additional_size)

    def item_repr(self, item):
        return text_repr(item)

    def get_item_length(self):
        return 8, ptr.LIST_SIZE_PTR

    def pack_item(self, listbuilder, i, item):
        offset = i * listbuilder.item_length
        if self.additional_size == 0:
            ptr = listbuilder.alloc_data(offset, item)
        else:
            ptr = listbuilder.alloc_text(offset, item)
        packed = pack_int64(ptr)
        return packed


class ListItemType(ItemType):

    def __init__(self, inner_item_type):
        self.inner_item_type = inner_item_type

    def get_type(self):
        return ('list', self.inner_item_type)

    def read_item(self, lst, i):
        offset = lst._offset + (i*8)
        p = lst._buf.read_ptr(offset)
        if ptr.kind(p) == ptr.FAR:
            raise NotImplementedError('FAR pointers not supported here')
        obj = List.__new__(List)
        obj._init_from_buffer(lst._buf,
                              ptr.deref(p, offset),
                              ptr.list_size_tag(p),
                              ptr.list_item_count(p),
                              self.inner_item_type)
        return obj

    def item_repr(self, item):
        return item.shortrepr()

    def get_item_length(self):
        return 8, ptr.LIST_SIZE_PTR

    def pack_item(self, listbuilder, i, item):
        offset = i * listbuilder.item_length
        ptr = listbuilder.alloc_list(offset, self.inner_item_type, item)
        packed = pack_int64(ptr)
        return packed



if PYX:
    # on CPython, we use prebuilt ItemType instances, as it is costly to
    # allocate a new one every time we create a List object. See also
    # misc.py:Type.list_item_type()
    #
    # Moreover, we need to explicitly create each one, because if we use
    # metaprogramming Cython cannot assign them a static type :(
    void_list_item_type = VoidItemType()
    bool_list_item_type = BoolItemType()
    int8_list_item_type = PrimitiveItemType(Types.int8)
    uint8_list_item_type = PrimitiveItemType(Types.uint8)
    int16_list_item_type = PrimitiveItemType(Types.int16)
    uint16_list_item_type = PrimitiveItemType(Types.uint16)
    int32_list_item_type = PrimitiveItemType(Types.int32)
    uint32_list_item_type = PrimitiveItemType(Types.uint32)
    int64_list_item_type = PrimitiveItemType(Types.int64)
    uint64_list_item_type = PrimitiveItemType(Types.uint64)
    float32_list_item_type = PrimitiveItemType(Types.float32)
    float64_list_item_type = PrimitiveItemType(Types.float64)
    text_list_item_type = TextItemType(Types.text)
    data_list_item_type = TextItemType(Types.data)
