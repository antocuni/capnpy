/* This is the implementation of the ptr.py logic in C. It is wrapped by
   ptr.pxd and in turn by ptr.pyx. If you modify anything, make sure"

     1. to update ptr.pxd and ptr.pyx accordingly

     2. to keep ptr.py (the pure-python version) in sync

     3. to add a test to test_ptr.py, so that we test the behavior in both versions
*/

enum _PTR_KIND {
    PTR_STRUCT = 0,
    PTR_LIST = 1,
    PTR_FAR = 2
};

enum _PTR_LIST_SIZE {
    PTR_LIST_SIZE_VOID = 0,
    PTR_LIST_SIZE_BIT = 1,
    PTR_LIST_SIZE_8 = 2,
    PTR_LIST_SIZE_16 = 3,
    PTR_LIST_SIZE_32 = 4,
    PTR_LIST_SIZE_64 = 5,
    PTR_LIST_SIZE_PTR = 6,
    PTR_LIST_SIZE_COMPOSITE = 7
};

#define LONGBITS (sizeof(long)*8)
#define CAST_AS_SIGNED(x, bits) (((long)x) << (LONGBITS-bits) >> (LONGBITS-bits))

// generic pointer
#define PTR_NEW_GENERIC(kind, offset, extra) ((extra)<<32 | (offset)<<2 | (kind))
#define PTR_KIND(ptr) ((ptr) & 0x3)
#define PTR_OFFSET(ptr) (CAST_AS_SIGNED((ptr)>>2 & 0x3fffffff, 30))
#define PTR_EXTRA(ptr) ((ptr)>>32)
#define PTR_DEREF(ptr, ofs) ((ofs) + (PTR_OFFSET(ptr)+1)*8)

// struct pointer
#define PTR_NEW_STRUCT(offset, data_size, ptrs_size)   \
    ((((long)ptrs_size) << 48)                  |      \
     (((long)data_size) << 32 & 0xffff00000000) |      \
     (((long)offset)    <<  2 & 0xfffffffc)     |      \
     PTR_STRUCT)

#define PTR_STRUCT_DATA_SIZE(ptr) ((ptr)>>32 & 0xffff)
#define PTR_STRUCT_PTRS_SIZE(ptr) ((ptr)>>48 & 0xffff)

// list pointer
#define PTR_NEW_LIST(ptr_offset, size_tag, item_count)    \
    ((((long)item_count) << 35)               |           \
     (((long)size_tag)   << 32 & 0x700000000) |           \
     (((long)ptr_offset) <<  2 & 0xfffffffc)  |           \
     PTR_LIST)

#define PTR_LIST_SIZE_TAG(ptr) ((ptr)>>32 & 0x7)
#define PTR_LIST_ITEM_COUNT(ptr) ((ptr)>>35 & 0x1fffffff)

// far pointer
#define PTR_NEW_FAR(landing_pad, offset, target)                  \
    ((((long)target)      << 32)              |                   \
     (((long)offset)      <<  3 & 0xfffffff8) |                   \
     (((long)landing_pad) <<  2 & 0x4)        |                   \
     PTR_FAR)

#define PTR_FAR_LANDING_PAD(ptr) ((ptr)>>2 & 1)
#define PTR_FAR_OFFSET(ptr) ((ptr)>>3 & 0x1fffffff)
#define PTR_FAR_TARGET(ptr) ((ptr)>>32 & 0xffffffff)

#define ROUND_UP_TO_WORD(i) (((i) + (8 - 1)) & -8)
