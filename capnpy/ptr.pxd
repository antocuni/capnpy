cdef extern from "ptr.h":
    cdef int STRUCT "_STRUCT"
    cdef int LIST "_LIST"
    cdef int FAR "_FAR"
    cdef int LIST_SIZE_BIT "_LIST_SIZE_BIT"
    cdef int LIST_SIZE_8 "_LIST_SIZE_8"
    cdef int LIST_SIZE_16 "_LIST_SIZE_16"
    cdef int LIST_SIZE_32 "_LIST_SIZE_32"
    cdef int LIST_SIZE_64 "_LIST_SIZE_64"
    cdef int LIST_SIZE_PTR "_LIST_SIZE_PTR"
    cdef int LIST_SIZE_COMPOSITE "_LIST_SIZE_COMPOSITE"

cpdef long as_signed(long x, char bits)
cpdef long new_generic(long kind, long offset, long extra)
cpdef long kind(long ptr)
cpdef long offset(long ptr)
cpdef long extra(long ptr)
cpdef long deref(long ptr, long ofs)
cpdef long new_struct(long offset, long data_size, long ptrs_size)
cpdef long struct_data_size(long ptr)
cpdef long struct_ptrs_size(long ptr)
cpdef long new_list(long ptr_offset, long size_tag, long item_count)
cpdef long list_size_tag(long ptr)
cpdef long list_item_count(long ptr)
cpdef long new_far(long landing_pad, long offset, long target)
cpdef long far_landing_pad(long ptr)
cpdef long far_offset(long ptr)
cpdef long far_target(long ptr)
