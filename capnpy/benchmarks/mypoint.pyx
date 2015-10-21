from capnpy.blob cimport Blob
from capnpy.unpack cimport __unpack_primitive_fast as upf

cdef class MyPoint(Blob):

    @classmethod
    def _allocate(cls):
        return MyPoint.__new__(cls)

    property x:
        def __get__(self):
            return upf('q', self._buf, self._offset+0)

    property y:
        def __get__(self):
            return upf('q', self._buf, self._offset+8)


