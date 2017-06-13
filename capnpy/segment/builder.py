import struct
from capnpy import ptr
from capnpy.packing import mychr
from capnpy.printer import print_buffer

class SegmentBuilder(object):

    def __init__(self, length=None):
        self.buf = bytearray()

    def get_length(self):
        return len(self.buf)

    def as_string(self):
        return str(self.buf)

    def _print(self):
        print_buffer(self.as_string())

    def write_generic(self, ifmt, i, value):
        struct.pack_into(mychr(ifmt), self.buf, i, value)

    def write_int8(self, i, value):
        struct.pack_into('b', self.buf, i, value)

    def write_uint8(self, i, value):
        struct.pack_into('B', self.buf, i, value)

    def write_int16(self, i, value):
        struct.pack_into('h', self.buf, i, value)

    def write_uint16(self, i, value):
        struct.pack_into('H', self.buf, i, value)

    def write_int32(self, i, value):
        struct.pack_into('i', self.buf, i, value)

    def write_uint32(self, i, value):
        struct.pack_into('I', self.buf, i, value)

    def write_int64(self, i, value):
        struct.pack_into('q', self.buf, i, value)

    def write_uint64(self, i, value):
        struct.pack_into('Q', self.buf, i, value)

    def write_float32(self, i, value):
        struct.pack_into('f', self.buf, i, value)

    def write_float64(self, i, value):
        struct.pack_into('d', self.buf, i, value)

    def write_bool(self, byteoffset, bitoffset, value):
        current = struct.unpack_from('B', self.buf, byteoffset)[0]
        current |= (value << bitoffset)
        struct.pack_into('B', self.buf, byteoffset, current)

    def write_slice(self, i, src, start, n):
        self.buf[i:i+n] = src.buf[start:start+n]

    def allocate(self, length):
        # XXX: check whether there is a better method to zero-extend the array in PyPy
        result = len(self.buf)
        self.buf += '\x00'*length
        return result

    def alloc_struct(self, pos, data_size, ptrs_size):
        """
        Allocate a new struct of the given size, and write the resulting pointer
        at position i. Return the newly allocated position.
        """
        length = (data_size+ptrs_size) * 8
        result = self.allocate(length)
        offet = result - (pos+8)
        p = ptr.new_struct(offet/8, data_size, ptrs_size)
        self.write_int64(pos, p)
        return result

    def alloc_list(self, pos, size_tag, item_count, body_length):
        """
        Allocate a new list of the given size, and write the resulting pointer
        at position i. Return the newly allocated position.
        """
        body_length = ptr.round_up_to_word(body_length)
        result = self.allocate(body_length)
        offet = result - (pos+8)
        p = ptr.new_list(offet/8, size_tag, item_count)
        self.write_int64(pos, p)
        return result

    def alloc_text(self, pos, s, trailing_zero=1):
        if s is None:
            self.write_int64(pos, 0)
            return -1
        n = len(s)
        nn = n + trailing_zero
        result = self.alloc_list(pos, ptr.LIST_SIZE_8, nn, nn)
        self.buf[result:result+n] = s
        # there is no need to write the trailing 0 as the byte is already
        # guaranteed to be 0
        return result

    def alloc_data(self, pos, s):
        return self.alloc_text(pos, s, trailing_zero=0)

    def copy_from_struct(self, dst_pos, structcls, value):
        if value is None:
            self.write_int64(dst_pos, 0)
            return
        if not isinstance(value, structcls):
            raise TypeError("Expected %s instance, got %s" %
                            (structcls.__class__.__name__, value))
        self.copy_from_pointer(dst_pos, value._seg, value._as_pointer(0), 0)

    def copy_from_pointer(self, dst_pos, src, p, src_pos):
        return copy_pointer(src, p, src_pos, self, dst_pos)

    def copy_inline_struct(self, dst_pos, src, p, src_pos):
        """
        Similar to copy_from_pointer but:
          1. it assumes that p is a pointer to a struct

          2. it does NOT allocate a new struct in dst_pos: instead, it writes
             the struct directly into dst_pos
        """
        return _copy_struct_inline(src, p, src_pos, self, dst_pos)

    def copy_from_list(self, pos, item_type, lst):
        return copy_from_list(self, pos, item_type, lst)

from capnpy.segment._copy_pointer import copy_pointer, _copy_struct_inline
from capnpy.segment._copy_list import copy_from_list
