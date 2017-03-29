cimport cython
from capnpy.segment.base cimport BaseSegment
from capnpy cimport ptr
from capnpy cimport _hash


cdef class Segment(BaseSegment):
    cpdef long read_ptr(self, long offset)
    cpdef read_far_ptr(self, long offset)

    @cython.locals(p=long, start=long, end=long)
    cpdef read_str(self, long p, long offset, default_, int additional_size)

    @cython.locals(p=long, start=long, size=long)
    cpdef long hash_str(self, long p, long offset, long default_, int additional_size) except -1


cdef class MultiSegment(Segment):
    cdef readonly object segment_offsets
