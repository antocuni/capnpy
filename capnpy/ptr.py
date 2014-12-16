import struct

class Ptr(int):
    ## lsb                      generic pointer                      msb
    ## +-+-----------------------------+-------------------------------+
    ## |A|             B               |               C               |
    ## +-+-----------------------------+-------------------------------+
    ##
    ## A (2 bits) = 0, pointer kind (0 for struct, 1 for list)
    ## B (30 bits) = Offset, in words, from the end of the pointer to the
    ##     start of the struct's data section.  Signed.
    ## C (32 bits) = extra info, depends on the kind

    @classmethod
    def new(cls, kind, offset, extra):
        ptr = 0
        ptr |= extra << 32
        ptr |= offset << 2
        ptr |= kind
        return cls(ptr)

    @classmethod
    def from_bytes(cls, s):
        ptr = struct.unpack('q', s)[0]
        return cls(ptr)

    @property
    def kind(self):
        return self & 0x3

    @property
    def offset(self):
        return self>>2 & 0x3fffffff

    @property
    def extra(self):
        return self>>32

    def deref(self, offset):
        """
        Compute the offset of the object pointed to, assuming that the Ptr itself
        is at ``offset``
        """
        # the +1 is needed because the offset is measured from the end of the
        # pointer itself
        return offset + (self.offset+1)*8

    def specialize(self):
        """
        Return a StructPtr or ListPtr, depending on self.kind
        """
        kind = self.kind
        if kind == StructPtr.KIND:
            return StructPtr(self)
        elif kind == ListPtr.KIND:
            return ListPtr(self)
        else:
            raise ValueError("Unknown ptr kind: %d" % kind)


class StructPtr(Ptr):
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
        ptr |= ptrs_size << 48
        ptr |= data_size << 32
        ptr |= offset << 2
        ptr |= cls.KIND
        return cls(ptr)

    @property
    def data_size(self):
        return self>>32 & 0xffff

    @property
    def ptrs_size(self):
        return self>>48 & 0xffff


class ListPtr(Ptr):
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

    # size tag
    SIZE_BIT = 1
    SIZE_8 = 2
    SIZE_16 = 3
    SIZE_32 = 4
    SIZE_64 = 5
    SIZE_PTR = 6
    SIZE_COMPOSITE = 7

    # map each size tag to the corresponding length in bytes. SIZE_BIT is
    # None, as it is handled specially
    SIZE_LENGTH = (None, None, 1, 2, 4, 8, 8)

    @classmethod
    def new(cls, ptr_offset, size_tag, item_count):
        ptr = 0
        ptr |= item_count << 35
        ptr |= size_tag << 32
        ptr |= ptr_offset << 2
        ptr |= cls.KIND
        return cls(ptr)

    @property
    def size_tag(self):
        return self>>32 & 0x7

    @property
    def item_count(self):
        return self>>35
