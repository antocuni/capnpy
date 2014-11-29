class PtrStruct(int):
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
    def new(cls, offset, data_size, ptrs_size):
        ptr = 0
        ptr |= ptrs_size/8 << 48
        ptr |= data_size/8 << 32
        ptr |= offset/8 << 2
        ptr |= cls.KIND
        return cls(ptr)

    @property
    def kind(self):
        return self & 0x3

    @property
    def offset(self):
        return self>>2 & 0x3fffffff

    @property
    def data_size(self):
        return self>>32 & 0xffff

    @property
    def ptrs_size(self):
        return self>>48 & 0xffff


class PtrList(int):
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
    def new(cls, ptr_offset, size_tag, item_count):
        ptr = 0
        ptr |= item_count << 35
        ptr |= size_tag << 32
        ptr |= ptr_offset/8 << 2
        ptr |= cls.KIND
        return ptr

    @property
    def kind(self):
        return self & 0x3

    @property
    def offset(self):
        return self>>2 & 0x3fffffff

    @property
    def size_tag(self):
        return self>>32 & 0x7

    @property
    def item_count(self):
        return self>>35
