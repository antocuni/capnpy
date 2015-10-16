from capnpy.blob cimport Blob
from capnpy.unpack cimport __unpack_primitive_fast as upf

cdef class MyPoint(Blob):

    @classmethod
    def from_buffer(cls, buf, offset, segment_offsets):
        self = MyPoint.__new__(cls)
        self._init(buf, offset, segment_offsets)
        return self

    property x:
        def __get__(self):
            return upf('q', self._buf, self._offset+0)

    property y:
        def __get__(self):
            return upf('q', self._buf, self._offset+8)


