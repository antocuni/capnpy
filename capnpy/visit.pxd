import cython
from capnpy cimport ptr
from capnpy.segment cimport Segment

cpdef long end_of(Segment buf, long p, long offset) except -2
cpdef long is_compact(Segment buf, long p, long offset) except -2

cdef class Visitor(object):

    cdef long visit(self, Segment buf, long p, long offset) except -2

    cdef long visit_struct(self, Segment buf, long p, long offset,
                           long data_size, long ptrs_size) except -2

    cdef long visit_list_composite(self, Segment buf, long p, long offset,
                                   long count, long data_size, long ptrs_size) except -2

    cdef long visit_list_ptr(self, Segment buf, long p, long offset,
                             long count) except -2

    cdef long visit_list_primitive(self, Segment buf, long p, long offset,
                                   long item_size, long count) except -2

    cdef long visit_list_bit(self, Segment buf, long p, long offset,
                             long count) except -2


cdef class EndOf(Visitor):

    @cython.locals(i=long, p2_offset=long, p2=long)
    cdef long visit_ptrs(self, Segment buf, long offset, long ptrs_size) except -2

    @cython.locals(end=long)
    cdef long visit_struct(self, Segment buf, long p, long offset,
                           long data_size, long ptrs_size) except -2

    @cython.locals(item_size=long, i=long)
    cdef long visit_list_composite(self, Segment buf, long p, long offset,
                                   long count, long data_size, long ptrs_size) except -2

    @cython.locals(count=long, end=long)
    cdef long visit_list_ptr(self, Segment buf, long p, long offset,
                             long count) except -2

    @cython.locals(count=long, bytes_length=long, extra_bits=long)
    cdef long visit_list_bit(self, Segment buf, long p, long offset,
                             long count) except -2


cdef class IsCompact(Visitor):
    @cython.locals(i=long, p2_offset=long, p2=long)
    cdef long start_of_ptrs(self, Segment buf, long offset, long ptrs_size) except -2

    @cython.locals(item_size=long, end_of_items=long, i=long)
    cdef long visit_list_composite(self, Segment buf, long p, long offset,
                                   long count, long data_size, long ptrs_size) except -2




cpdef EndOf _end_of
cpdef IsCompact _is_compact
