class PtrStruct(object):
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

    KIND = 0

    @classmethod
    def unpack(cls, ptr):
        ptr_kind  = ptr & 0x3
        ptr_offset = ptr>>2 & 0x3fffffff
        data_size = ptr>>32 & 0xffff
        ptrs_size = ptr>>48 & 0xffff
        assert ptr_kind == cls.KIND
        return ptr_offset, data_size, ptrs_size

    @classmethod
    def unpack_offset(cls, ptr):
        # we partially replicate the logic of _unpack_ptrstruct, because in
        # the common case it's not needed to decode data_size and ptrs_size
        ptr_kind  = ptr & 0x3
        ptr_offset = ptr>>2 & 0x3fffffff
        assert ptr_kind == cls.KIND
        return ptr_offset

    @classmethod
    def pack(cls, ptr_offset, data_size, ptrs_size):
        ptr = 0
        ptr |= ptrs_size/8 << 48
        ptr |= data_size/8 << 32
        ptr |= ptr_offset/8 << 2
        ptr |= cls.KIND
        return ptr



class PtrList(object):
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

    KIND = 1

    @classmethod
    def unpack(cls, ptr):
        ptr_kind  = ptr & 0x3
        ptr_offset = ptr>>2 & 0x3fffffff
        item_size_tag = ptr>>32 & 0x7
        item_count = ptr>>35
        assert ptr_kind == cls.KIND
        return ptr_offset, item_size_tag, item_count

    @classmethod
    def pack(cls, ptr_offset, size_tag, item_count):
        ptr = 0
        ptr |= item_count << 35
        ptr |= size_tag << 32
        ptr |= ptr_offset/8 << 2
        ptr |= cls.KIND
        return ptr
