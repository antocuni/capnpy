import struct
from capnpy.ptr import PtrStruct, PtrList

class Types(object):
    Int64 = 'q'
    Float64 = 'd'

class Blob(object):

    # pointer kind
    PTR_STRUCT = PtrStruct.KIND
    PTR_LIST = 1

    # list item size tag
    LIST_BIT = 1
    LIST_8 = 2
    LIST_16 = 3
    LIST_32 = 4
    LIST_64 = 5
    LIST_PTR = 6
    LIST_COMPOSITE = 7
    # map each LIST size tag to the corresponding size in bytes. LIST_BIT is None, as
    # it is handled specially
    LIST_SIZE = (None, None, 1, 2, 4, 8, 8)

    def __init__(self):
        raise NotImplementedError('Cannot instantiate Blob directly; '
                                  'use Blob.from_buffer instead')

    @classmethod
    def from_buffer(cls, buf, offset):
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
        offset, item_size, item_count = self._deref_ptrlist(offset)
        if offset is None:
            return None
        return listcls.from_buffer(self._buf, self._offset+offset,
                                   item_size, item_count, item_type)

    def _read_string(self, offset):
        offset, item_size, item_count = self._deref_ptrlist(offset)
        if offset is None:
            return None
        assert item_size == 1
        start = self._offset + offset
        end = start + item_count - 1
        return self._buf[start:end]

    def _deref_ptrstruct(self, offset):
        ptr = self._read_primitive(offset, Types.Int64)
        if ptr == 0:
            return None
        ptr_offset = PtrStruct.unpack_offset(ptr)
        # the +1 is needed because the offset is measured from the end of the
        # pointer itself
        offset = offset + (ptr_offset+1)*8
        return offset

    def _deref_ptrlist(self, offset):
        """
        Dereference a list pointer at the given offset.  It returns a tuple
        (offset, item_size, item_count):

        - offset is where the list items start, from the start of the blob
        - item_size: the size IN BYTES of each element
        - item_count: the total number of elements
        """
        ptr = self._read_primitive(offset, Types.Int64)
        if ptr == 0:
            return None, None, None
        ptr_offset, item_size_tag, item_count = PtrList.unpack(ptr)
        offset = offset + (ptr_offset+1)*8
        if item_size_tag == self.LIST_COMPOSITE:
            tag = self._read_primitive(offset, Types.Int64)
            item_count, data_size, ptrs_size = PtrStruct.unpack(tag)
            item_size = (data_size+ptrs_size)*8
            offset += 8
        elif item_size_tag == self.LIST_BIT:
            raise ValueError('Lists of bits are not supported')
        else:
            item_size = self.LIST_SIZE[item_size_tag]
        return offset, item_size, item_count
