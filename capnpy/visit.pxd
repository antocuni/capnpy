import cython
from capnpy cimport ptr
from capnpy.blob cimport CapnpBuffer

cpdef long end_of(CapnpBuffer buf, long p, long offset) except -2

@cython.locals(data_size=long, ptrs_size=long, end=long)
cdef long end_of_struct(CapnpBuffer buf, long p, long offset)

@cython.locals(i=long, p2_offset=long, p2=long)
cdef long end_of_ptrs(CapnpBuffer buf, long offset, long ptrs_size)

@cython.locals(count=long, data_size=long, ptrs_size=long, item_size=long, i=long)
cdef long end_of_list_composite(CapnpBuffer buf, long p, long offset)

@cython.locals(count=long, end=long)
cdef long end_of_list_ptr(CapnpBuffer buf, long p, long offset)

@cython.locals(count=long, item_size=long)
cdef long end_of_list_primitive(CapnpBuffer buf, long p, long offset) except -2

@cython.locals(count=long, bytes_length=long, extra_bits=long)
cdef long end_of_list_bit(CapnpBuffer buf, long p, long offset)

