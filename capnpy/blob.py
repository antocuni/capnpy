import struct

class Blob(object):

    # pointer kind
    PTR_STRUCT = 0
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

    def __init__(self, buf, offset):
        self._buf = buf
        self._offset = offset

    def _read_primitive(self, offset, fmt):
        return struct.unpack_from(fmt, self._buf, self._offset+offset)[0]

    def _read_int64(self, offset):
        """
        Read an int64 at the given offset
        """
        return self._read_primitive(offset, '<q')

    def _read_float64(self, offset):
        """
        Read an int64 at the given offset
        """
        return self._read_primitive(offset, 'd')

    def _read_struct(self, offset, structcls):
        """
        Read and dereference a struct pointer at the given offset.  It returns an
        instance of ``cls`` pointing to the dereferenced struct.
        """
        struct_offset = self._deref_ptrstruct(offset)
        return structcls(self._buf, self._offset+struct_offset)

    def _read_list(self, offset, listcls, itemcls=None):
        offset, item_size, item_count = self._deref_ptrlist(offset)
        return listcls(self._buf, self._offset+offset, item_size, item_count, itemcls)

    def _read_string(self, offset):
        offset, item_size, item_count = self._deref_ptrlist(offset)
        assert item_size == 1
        start = self._offset + offset
        end = start + item_count - 1
        return self._buf[start:end]

    def _unpack_ptrstruct(self, offset):
        ## lsb                      struct pointer                       msb
        ## +-+-----------------------------+---------------+---------------+
        ## |A|             B               |       C       |       D       |
        ## +-+-----------------------------+---------------+---------------+
        ##
        ## A (2 bits) = 0, to indicate that this is a struct pointer.
        ## B (30 bits) = Offset, in words, from the end of the pointer to the
        ##     start of the struct's data section.  Signed.
        ## C (16 bits) = Size of the struct's data section, in words.
        ## D (16 bits) = Size of the struct's pointer section, in words.
        ptr = self._read_int64(offset)
        ptr_kind  = ptr & 0x3
        ptr_offset = ptr>>2 & 0x3fffffff
        data_size = ptr>>32 & 0xffff
        ptrs_size = ptr>>48 & 0xffff
        assert ptr_kind == self.PTR_STRUCT
        return ptr_offset, data_size, ptrs_size

    def _deref_ptrstruct(self, offset):
        # we partially replicate the logic of _unpack_ptrstruct, because in
        # the common case it's not needed to decode data_size and ptrs_size
        ptr = self._read_int64(offset)
        ptr_kind  = ptr & 0x3
        ptr_offset = ptr>>2 & 0x3fffffff
        assert ptr_kind == self.PTR_STRUCT
        # the +1 is needed because the offset is measured from the end of the
        # pointer itself
        offset = offset + (ptr_offset+1)*8
        return offset

    def _unpack_ptrlist(self, offset):
        ## lsb                       list pointer                        msb
        ## +-+-----------------------------+--+----------------------------+
        ## |A|             B               |C |             D              |
        ## +-+-----------------------------+--+----------------------------+
        ##
        ## A (2 bits) = 1, to indicate that this is a list pointer.
        ## B (30 bits) = Offset, in words, from the end of the pointer to the
        ##     start of the first element of the list.  Signed.
        ## C (3 bits) = Size of each element:
        ##     0 = 0 (e.g. List(Void))
        ##     1 = 1 bit
        ##     2 = 1 byte
        ##     3 = 2 bytes
        ##     4 = 4 bytes
        ##     5 = 8 bytes (non-pointer)
        ##     6 = 8 bytes (pointer)
        ##     7 = composite (see below)
        ## D (29 bits) = Number of elements in the list, except when C is 7
        ptr = self._read_int64(offset)
        ptr_kind  = ptr & 0x3
        ptr_offset = ptr>>2 & 0x3fffffff
        item_size_tag = ptr>>32 & 0x7
        item_count = ptr>>35
        assert ptr_kind == self.PTR_LIST
        #offset = offset + (ptr_offset+1)*8
        return ptr_offset, item_size_tag, item_count

    def _deref_ptrlist(self, offset):
        """
        Dereference a list pointer at the given offset.  It returns a tuple
        (offset, item_size, item_count):

        - offset is where the list items start, from the start of the blob
        - item_size: the size IN BYTES of each element
        - item_count: the total number of elements
        """
        ptr_offset, item_size_tag, item_count = self._unpack_ptrlist(offset)
        offset = offset + (ptr_offset+1)*8
        if item_size_tag == self.LIST_COMPOSITE:
            item_count, data_size, ptrs_size = self._unpack_ptrstruct(offset)
            item_size = (data_size+ptrs_size)*8
            offset += 8
        elif item_size_tag == self.LIST_BIT:
            raise ValueError('Lists of bits are not supported')
        else:
            item_size = self.LIST_SIZE[item_size_tag]
        return offset, item_size, item_count
