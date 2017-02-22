import cython
from capnpy cimport ptr
from capnpy.blob cimport CapnpBuffer

cpdef long end_of(CapnpBuffer buf, long p, long offset) except -2
cpdef long is_compact(CapnpBuffer buf, long p, long offset) except -2

cdef class Visitor(object):

    cdef long visit(self, CapnpBuffer buf, long p, long offset) except -2

    cdef long visit_struct(self, CapnpBuffer buf, long p, long offset,
                           long data_size, long ptrs_size) except -2

    cdef long visit_list_composite(self, CapnpBuffer buf, long p, long offset,
                                   long count, long data_size, long ptrs_size) except -2

    cdef long visit_list_ptr(self, CapnpBuffer buf, long p, long offset,
                             long count) except -2

    cdef long visit_list_primitive(self, CapnpBuffer buf, long p, long offset,
                                   long item_size, long count) except -2

    cdef long visit_list_bit(self, CapnpBuffer buf, long p, long offset,
                             long count) except -2


cdef class EndOf(Visitor):

    @cython.locals(i=long, p2_offset=long, p2=long)
    cdef long visit_ptrs(self, CapnpBuffer buf, long offset, long ptrs_size) except -2

    @cython.locals(end=long)
    cdef long visit_struct(self, CapnpBuffer buf, long p, long offset,
                           long data_size, long ptrs_size) except -2

    @cython.locals(item_size=long, i=long)
    cdef long visit_list_composite(self, CapnpBuffer buf, long p, long offset,
                                   long count, long data_size, long ptrs_size) except -2

    @cython.locals(count=long, end=long)
    cdef long visit_list_ptr(self, CapnpBuffer buf, long p, long offset,
                             long count) except -2

    @cython.locals(count=long, bytes_length=long, extra_bits=long)
    cdef long visit_list_bit(self, CapnpBuffer buf, long p, long offset,
                             long count) except -2


cdef class IsCompact(Visitor):
    @cython.locals(i=long, p2_offset=long, p2=long)
    cdef long start_of_ptrs(self, CapnpBuffer buf, long offset, long ptrs_size) except -2

    @cython.locals(item_size=long, end_of_items=long, i=long)
    cdef long visit_list_composite(self, CapnpBuffer buf, long p, long offset,
                                   long count, long data_size, long ptrs_size) except -2




cpdef EndOf _end_of
cpdef IsCompact _is_compact
