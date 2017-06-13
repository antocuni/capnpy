import cython
from capnpy cimport ptr
from capnpy.segment.segment cimport Segment

cpdef long end_of(Segment buf, long p, long offset) except -2

cdef class NotCompact(Exception):
    pass

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

    @cython.locals(i=long, p_offset=long, p=long)
    cdef long visit_ptrs(self, Segment buf, long offset, long ptrs_size,
                         long current_end) except -2

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


cpdef EndOf _end_of
