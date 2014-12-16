# glossary:
#
#   - size: they are always expressed in WORDS
#   - length: they are always expressed in BYTES


import struct
from capnpy.ptr import Ptr, StructPtr, ListPtr

class Types(object):
    Int8 = 'b'
    Int64 = 'q'
    Float64 = 'd'

class Blob(object):
    """
    Base class to read a generic capnp object.

    Some features cannot be used directly, because you need to specify
    __data_size__ and __ptrs_size__. You can either:

      1) subclass Blob and add __data_size__, __ptrs_size__ as class
         attributes

      2) instantiate GenericBlob, and pass them to the constructor
    """
    
    def __init__(self):
        raise NotImplementedError('Cannot instantiate Blob directly; '
                                  'use Blob.from_buffer instead')

    @classmethod
    def from_buffer(cls, buf, offset=0):
        self = cls.__new__(cls)
        self._buf = buf
        self._offset = offset
        return self

    def _read_primitive(self, offset, fmt):
        return struct.unpack_from('<' + fmt, self._buf, self._offset+offset)[0]

    def _read_struct(self, offset, structcls):
        """
        Read and dereference a struct pointer at the given offset.  It returns an
        instance of ``cls`` pointing to the dereferenced struct.
        """
        struct_offset = self._deref_ptrstruct(offset)
        if struct_offset is None:
            return None
        return structcls.from_buffer(self._buf, self._offset+struct_offset)

    def _read_list(self, offset, listcls, item_type):
        offset, item_length, item_count = self._deref_ptrlist(offset)
        if offset is None:
            return None
        return listcls.from_buffer(self._buf, self._offset+offset,
                                   item_length, item_count, item_type)

    def _read_string(self, offset):
        offset, item_length, item_count = self._deref_ptrlist(offset)
        if offset is None:
            return None
        assert item_length == 1
        start = self._offset + offset
        end = start + item_count - 1
        return self._buf[start:end]

    def _read_ptr(self, offset):
        ptr = self._read_primitive(offset, Types.Int64)
        return Ptr(ptr)

    def _deref_ptrstruct(self, offset):
        ptr = self._read_primitive(offset, Types.Int64)
        if ptr == 0:
            return None
        ptr = StructPtr(ptr)
        return ptr.deref(offset)

    def _deref_ptrlist(self, offset):
        """
        Dereference a list pointer at the given offset.  It returns a tuple
        (offset, item_length, item_count):

        - offset is where the list items start, from the start of the blob
        - item_length: the length IN BYTES of each element
        - item_count: the total number of elements
        """
        ptr = self._read_primitive(offset, Types.Int64)
        if ptr == 0:
            return None, None, None
        ptr = ListPtr(ptr)
        offset = ptr.deref(offset)
        item_size_tag = ptr.size_tag
        item_count = ptr.item_count
        if item_size_tag == ListPtr.SIZE_COMPOSITE:
            tag = self._read_primitive(offset, Types.Int64)
            tag = StructPtr(tag)
            item_count = tag.offset
            item_length = (tag.data_size+tag.ptrs_size)*8
            offset += 8
        elif item_size_tag == ListPtr.SIZE_BIT:
            raise ValueError('Lists of bits are not supported')
        else:
            item_length = ListPtr._SIZE_LENGTH[item_size_tag]
        return offset, item_length, item_count


    def _ptr_by_index(self, i):
        offset = (self.__data_size__ + i) * 8
        return offset, self._read_ptr(offset)

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
        ptr_offset, ptr = self._ptr_by_index(0)
        return self._offset + ptr.deref(ptr_offset)

    def _get_extra_end(self):
        # see doc/normalize.rst for an explanation of why we can compute the
        # extra range this way
        if self.__ptrs_size__ == 0:
            return self._get_body_end()
        ptr_offset, ptr = self._ptr_by_index(self.__ptrs_size__ - 1)
        blob_offet = ptr.deref(ptr_offset)
        data_size, ptrs_size = ptr.get_size()
        blob = GenericBlob.from_buffer_and_size(self._buf, self._offset+blob_offet,
                                                data_size, ptrs_size)
        return blob._get_extra_end()
        

class GenericBlob(Blob):

    @classmethod
    def from_buffer_and_size(cls, buf, offset, data_size, ptrs_size):
        self = cls.from_buffer(buf, offset)
        self.__data_size__ = data_size
        self.__ptrs_size__ = ptrs_size
        return self
