cdef extern from "ptr.h":
    cdef int STRUCT "PTR_STRUCT"
    cdef int LIST "PTR_LIST"
    cdef int FAR "PTR_FAR"
    cdef int LIST_SIZE_VOID "PTR_LIST_SIZE_VOID"
    cdef int LIST_SIZE_BIT "PTR_LIST_SIZE_BIT"
    cdef int LIST_SIZE_8 "PTR_LIST_SIZE_8"
    cdef int LIST_SIZE_16 "PTR_LIST_SIZE_16"
    cdef int LIST_SIZE_32 "PTR_LIST_SIZE_32"
    cdef int LIST_SIZE_64 "PTR_LIST_SIZE_64"
    cdef int LIST_SIZE_PTR "PTR_LIST_SIZE_PTR"
    cdef int LIST_SIZE_COMPOSITE "PTR_LIST_SIZE_COMPOSITE"

    long new_generic "PTR_NEW_GENERIC" (long kind, long offset, long extra)
    long kind "PTR_KIND" (long ptr)
    long offset "PTR_OFFSET" (long ptr)
    long extra "PTR_EXTRA" (long ptr)
    long deref "PTR_DEREF" (long ptr, long ofs)
    long new_struct "PTR_NEW_STRUCT" (long offset, long data_size, long ptrs_size)
    long struct_data_size "PTR_STRUCT_DATA_SIZE" (long ptr)
    long struct_ptrs_size "PTR_STRUCT_PTRS_SIZE" (long ptr)
    long new_list "PTR_NEW_LIST" (long ptr_offset, long size_tag, long item_count)
    long list_size_tag "PTR_LIST_SIZE_TAG" (long ptr)
    long list_item_count "PTR_LIST_ITEM_COUNT" (long ptr)
    long new_far "PTR_NEW_FAR" (long landing_pad, long offset, long target)
    long far_landing_pad "PTR_FAR_LANDING_PAD" (long ptr)
    long far_offset "PTR_FAR_OFFSET" (long ptr)
    long far_target "PTR_FAR_TARGET" (long ptr)
    long round_up_to_word "ROUND_UP_TO_WORD" (long i)

cpdef long list_item_length(long size_tag)
