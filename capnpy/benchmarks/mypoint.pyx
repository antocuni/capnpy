from capnpy.struct_ cimport Struct as Struct
from capnpy.unpack cimport __unpack_primitive_fast as upf

cdef class MyPoint(Struct):

    @classmethod
    def _allocate(cls):
        return MyPoint.__new__(cls)

    property x:
        def __get__(self):
            return upf('q', self._buf, self._offset+0)

    property y:
        def __get__(self):
            return upf('q', self._buf, self._offset+8)

