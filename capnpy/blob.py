# glossary:
#
#   - size: they are always expressed in WORDS
#   - length: they are always expressed in BYTES


import struct
import cython
import capnpy
from capnpy.util import extend
from capnpy.ptr import Ptr, StructPtr, ListPtr, FarPtr
from capnpy.type import Types
from capnpy.printer import BufferPrinter
from capnpy.unpack import unpack_primitive

PYX = cython.compiled

class CapnpBuffer(object):

    def __init__(self, s, segment_offsets):
        self.s = s
        self.segment_offsets = segment_offsets

    def read_primitive(self, offset, ifmt):
        return unpack_primitive(ifmt, self.s, offset)

    def read_raw_ptr(self, offset):
        ptr = self.read_primitive(offset, Types.int64.ifmt)
        return Ptr(ptr)

    def read_ptr(self, offset):
        ptr = self.read_raw_ptr(offset)
        if ptr.kind == FarPtr.KIND:
            ptr = ptr.specialize()
            return self._follow_far_ptr(ptr)
        return offset, ptr

    def _follow_far_ptr(self, ptr):
        """
        Read and return the ptr referenced by this far pointer
        """
        if self.segment_offsets is None:
            raise ValueError("Cannot follow a far pointer if there is no segment data")
        assert ptr.landing_pad == 0
        segment_start = self.segment_offsets[ptr.target] # in bytes
        offset  = segment_start + ptr.offset*8
        ptr = self.read_raw_ptr(offset)
        return offset, ptr


class Blob(object):
    """
    Abstract base class to read a generic capnp object.
    """

    @classmethod
    def __extend__(cls, newcls):
        return extend(cls)(newcls)

    def __init__(self, buf):
        if isinstance(buf, str):
            buf = CapnpBuffer(buf, None)
        self._buf = buf

    def _read_data(self, offset, t):
        # overridden by Struct and List
        raise NotImplementedError

    def _read_ptr(self, offset):
        # overridden by Struct and List
        raise NotImplementedError

    def _read_bit(self, offset, bitmask):
        val = self._read_data(offset, Types.uint8.ifmt)
        return bool(val & bitmask)

    def _read_enum(self, offset, enumtype):
        val = self._read_data(offset, Types.int16.ifmt)
        return enumtype(val)

    def _read_struct(self, offset, structcls, default_=None):
        """
        Read and dereference a struct pointer at the given offset.  It returns an
        instance of ``structcls`` pointing to the dereferenced struct.
        """
        offset, ptr = self._read_ptr(offset)
        if ptr == 0:
            return default_
        assert ptr.kind == StructPtr.KIND
        ptr = ptr.specialize()
        struct_offset = ptr.deref(offset)
        return structcls.from_buffer(self._buf,
                                     struct_offset,
                                     ptr.data_size,
                                     ptr.ptrs_size)


    def _read_list(self, offset, listcls, item_type, default_=None):
        offset, ptr = self._read_ptr(offset)
        if ptr == 0:
            return default_
        assert ptr.kind == ListPtr.KIND
        ptr = ptr.specialize()
        list_offset = ptr.deref(offset)
        return listcls.from_buffer(self._buf,
                                   list_offset,
                                   ptr.size_tag,
                                   ptr.item_count,
                                   item_type)

    def _read_str_text(self, offset, default_=None):
        return self._read_str_data(offset, default_, additional_size=-1)

    def _read_str_data(self, offset, default_=None, additional_size=0):
        offset, ptr = self._read_ptr(offset)
        if ptr == 0:
            return default_
        ptr = ptr.specialize()
        assert ptr.kind == ListPtr.KIND
        assert ptr.size_tag == ListPtr.SIZE_8
        start = ptr.deref(offset)
        end = start + ptr.item_count + additional_size
        return self._buf.s[start:end]

    def _read_list_or_struct(self, ptr_offset, default_=None):
        ptr_offset, ptr = self._read_ptr(ptr_offset)
        if ptr == 0:
            return default_
        ptr = ptr.specialize()
        blob_offet = ptr.deref(ptr_offset)
        if ptr.kind == StructPtr.KIND:
            Struct = capnpy.struct_.Struct
            return Struct.from_buffer(self._buf,
                                      blob_offet,
                                      ptr.data_size, ptr.ptrs_size)
        elif ptr.kind == ListPtr.KIND:
            List = capnpy.list.List
            return List.from_buffer(self._buf,
                                    blob_offet,
                                    ptr.size_tag,ptr.item_count, Blob)
        else:
            assert False, 'Unkwown pointer kind: %s' % ptr.kind

    def _print_buf(self, start=None, end='auto', **kwds):
        if start is None:
            start = self._data_offset
        if end == 'auto':
            end = self._get_body_end()
        elif end is None:
            end = len(self._buf)
        p = BufferPrinter(self._buf)
        p.printbuf(start=start, end=end, **kwds)


# that these two modules are used by _read_list_or_struct. We need to put them
# at the end because of circular references
import capnpy.struct_
import capnpy.list
