cdef class Ptr(int):
    cpdef deref(self, long offset)
    cpdef specialize(self)
    
cdef class StructPtr(Ptr):
    pass

cdef class ListPtr(Ptr):
    pass

cdef class FarPtr(Ptr):
    pass

