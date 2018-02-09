import cython
from capnpy cimport ptr
from capnpy.segment.segment cimport Segment

cpdef long endof(Segment seg, long p, long offset) except -2

@cython.locals(i=long, p_offset=long, p=long)
cdef long _endof_ptrs(Segment seg, long offset, long ptrs_size,
                     long current_end)

@cython.locals(end=long)
cdef long _endof_struct(Segment seg, long p, long offset,
                       long data_size, long ptrs_size)

@cython.locals(item_size=long, i=long)
cdef long _endof_list_composite(Segment seg, long p, long offset,
                               long count, long data_size, long ptrs_size)

@cython.locals(count=long, end=long)
cdef long _endof_list_ptr(Segment seg, long p, long offset,
                         long count)

cdef long _endof_list_primitive(Segment seg, long p, long offset,
                               long item_size, long count)


@cython.locals(count=long, bytes_length=long, extra_bits=long)
cdef long _endof_list_bit(Segment seg, long p, long offset,
                         long count)
