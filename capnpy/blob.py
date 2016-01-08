# glossary:
#
#   - size: they are always expressed in WORDS
#   - length: they are always expressed in BYTES


import struct
import capnpy
from capnpy.util import extend
from capnpy.ptr import Ptr, StructPtr, ListPtr, FarPtr
from capnpy.type import Types
from capnpy.printer import BufferPrinter
from capnpy.unpack import unpack_primitive

class Blob(object):
    """
    Base class to read a generic capnp object.
    """

    @classmethod
    def __extend__(cls, newcls):
        return extend(cls)(newcls)

    def __init__(self, buf, offset, segment_offsets):
        self._buf = buf
        self._offset = offset
        assert self._offset < len(self._buf)
        self._segment_offsets = segment_offsets

    def _read_primitive(self, offset, t):
        return unpack_primitive(t.fmt, self._buf, self._offset+offset)

    def _read_list(self, offset, listcls, item_type):
        offset, ptr = self._read_ptr(offset)
        if ptr is None:
            return None
        assert ptr.kind == ListPtr.KIND
        ptr = ptr.specialize()
        list_offset = ptr.deref(offset)
        return listcls.from_buffer(self._buf,
                                   self._offset+list_offset,
                                   self._segment_offsets,
                                   ptr.size_tag,
                                   ptr.item_count,
                                   item_type)

    def _read_string(self, offset):
        offset, ptr = self._read_ptr(offset)
        if ptr is None:
            return None
        ptr = ptr.specialize()
        assert ptr.kind == ListPtr.KIND
        assert ptr.size_tag == ListPtr.SIZE_8
        str_offset = ptr.deref(offset)
        start = self._offset + str_offset
        end = start + ptr.item_count - 1
        return self._buf[start:end]

    def _read_data_string(self, offset):
        offset, ptr = self._read_ptr(offset)
        if ptr is None:
            return None
        ptr = ptr.specialize()
        assert ptr.kind == ListPtr.KIND
        assert ptr.size_tag == ListPtr.SIZE_8
        str_offset = ptr.deref(offset)
        start = self._offset + str_offset
        end = start + ptr.item_count
        return self._buf[start:end]

    def _read_raw_ptr(self, offset):
        """
        Read a pointer at the specified offset
        """
        ptr = self._read_primitive(offset, Types.int64)
        return Ptr(ptr)

    def _read_group(self, groupcls):
        return groupcls.from_buffer(self._buf, self._offset,
                                    self._segment_offsets,
                                    self._data_size,
                                    self._ptrs_size)

    def _read_generic_pointer(self, ptr_offset):
        ptr = self._read_raw_ptr(ptr_offset)
        if ptr == 0:
            return None
        ptr = ptr.specialize()
        blob_offet = ptr.deref(ptr_offset)
        if ptr.kind == StructPtr.KIND:
            Struct = capnpy.struct_.Struct
            return Struct.from_buffer(self._buf,
                                      self._offset+blob_offet,
                                      self._segment_offsets,
                                      ptr.data_size, ptr.ptrs_size)
        elif ptr.kind == ListPtr.KIND:
            List = capnpy.list.List
            return List.from_buffer(self._buf,
                                    self._offset+blob_offet,
                                    self._segment_offsets,
                                    ptr.size_tag,ptr.item_count, Blob)
        else:
            assert False, 'Unkwown pointer kind: %s' % ptr.kind

    def _read_ptr(self, offset):
        ptr = self._read_raw_ptr(offset)
        if ptr == 0:
            return offset, None
        if ptr.kind == FarPtr.KIND:
            ptr = ptr.specialize()
            return ptr.follow(self)
        return offset, ptr

    def _print_buf(self, start=None, end='auto', **kwds):
        if start is None:
            start = self._offset
        if end == 'auto':
            end = self._get_body_end()
        elif end is None:
            end = len(self._buf)
        p = BufferPrinter(self._buf)
        p.printbuf(start=start, end=end, **kwds)


# make sure that these two modules are imported, they are used by
# _read_generic_pointer. We need to put them at the end because of circular
# references
import capnpy.struct_
import capnpy.list
