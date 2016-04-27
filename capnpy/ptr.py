# This is the pure python version. Note that it exists ptr.pyx, which is
# automatically used if you enable cython compilation. The two versions should
# stay in-sync, as they are supposed to implement the same API. Make sure that
# every feature you add is tested by test_ptr.

import sys
import struct
from pypytools.cast import as_signed

# The following constants above are declared as enums in ptr.pxd/ptr.h, so we
# cannot assign directly to them, else Cython produces a bogus C
# file. However, we want them to be defined here in case we are in pure-python
# mode.
STRUCT = 0
LIST = 1
FAR = 2
LIST_SIZE_BIT = 1
LIST_SIZE_8 = 2
LIST_SIZE_16 = 3
LIST_SIZE_32 = 4
LIST_SIZE_64 = 5
LIST_SIZE_PTR = 6
LIST_SIZE_COMPOSITE = 7
LIST_SIZE_LENGTH = (None, None, 1, 2, 4, 8, 8)

# error code to indicate that the fast path to get a pointer failed because
# it's a FAR pointer, and you should use the slower API to access it.  From
# the capnproto docs, this is guaranteed (for now) to be an invalid pointer:
#
## lsb                    capability pointer                     msb
## +-+-----------------------------+-------------------------------+
## |A|              B              |               C               |
## +-+-----------------------------+-------------------------------+
##
## A (2 bits) = 3, to indicate that this is an "other" pointer.
## B (30 bits) = 0, to indicate that this is a capability pointer.
##     (All other values are reserved for future use.)
## C (32 bits) = Index of the capability in the message's capability
##     table.
##
## Thus, -1 has kind==3, but B=-1 as well instead of 0. Technically it's a
## reserved value, but for now we can use it as a sentinel.
E_IS_FAR_POINTER = -1

## =================================================================
##
## lsb                      generic pointer                      msb
## +-+-----------------------------+-------------------------------+
## |A|             B               |               C               |
## +-+-----------------------------+-------------------------------+
##
## A (2 bits) = 0, pointer kind (0 for struct, 1 for list)
## B (30 bits) = Offset, in words, from the end of the pointer to the
##     start of the struct's data section.  Signed.
## C (32 bits) = extra info, depends on the kind
##
## =================================================================

def new_generic(kind, offset, extra):
    p = 0
    p |= extra << 32
    p |= offset << 2
    p |= kind
    return p

def kind(ptr):
    return ptr & 0x3

def offset(ptr):
    return as_signed(ptr>>2 & 0x3fffffff, 30)

def extra(ptr):
    return ptr>>32

def deref(ptr, ofs):
    """
    Compute the offset of the object pointed to, assuming that the pointer
    is at ``offset``
    """
    # the +1 is needed because the offset is measured from the end of the
    # pointer itptr
    return ofs + (offset(ptr)+1)*8


## =================================================================
##
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
##
## =================================================================

def new_struct(offset, data_size, ptrs_size):
    p = 0
    p |= ptrs_size << 48
    p |= data_size << 32
    p |= offset << 2
    p |= STRUCT
    return p

def struct_data_size(ptr):
    return ptr>>32 & 0xffff

def struct_ptrs_size(ptr):
    return ptr>>48 & 0xffff


## =================================================================
##
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
##
## =================================================================

def new_list(ptr_offset, size_tag, item_count):
    p = 0
    p |= item_count << 35
    p |= size_tag << 32
    p |= ptr_offset << 2
    p |= LIST
    return p

def list_size_tag(ptr):
    return ptr>>32 & 0x7

def list_item_count(ptr):
    return ptr>>35


## =================================================================
##
## lsb                        far pointer                        msb
## +-+-+---------------------------+-------------------------------+
## |A|B|            C              |               D               |
## +-+-+---------------------------+-------------------------------+

## A (2 bits) = 2, to indicate that this is a far pointer.
## B (1 bit) = 0 if the landing pad is one word, 1 if it is two words.
## C (29 bits) = Offset, in words, from the start of the target segment
##     to the location of the far-pointer landing-pad within that
##     segment.  Unsigned.
## D (32 bits) = ID of the target segment.  (Segments are numbered
##     sequentially starting from zero.)
##
## =================================================================

def new_far(landing_pad, offset, target):
    p = 0
    p |= target << 32
    p |= offset << 3
    p |= landing_pad << 2
    p |= FAR
    return p

def far_landing_pad(ptr):
    return ptr>>2 & 1

def far_offset(ptr):
    return ptr>>3 & 0x1fffffff

def far_target(ptr):
    return ptr>>32
