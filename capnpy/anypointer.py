from capnpy import ptr
from capnpy.blob import Blob

class AnyPointer(Blob):

    def __init__(self, buf, offset, p):
        self._init_from_pointer(buf, offset, p)

    def _init_from_pointer(self, buf, offset, p):
        self._init_blob(buf)
        self._offset = offset
        self._p = p

    def is_struct(self):
        return ptr.kind(self._p) == ptr.STRUCT

    def is_list(self):
        return ptr.kind(self._p) == ptr.LIST

    def as_struct(self, cls):
        if not self.is_struct():
            raise ValueError("This AnyPointer seems to point to a list")
        res = cls.__new__(cls)
        res._init_from_pointer(self._seg, self._offset, self._p)
        return res

    def as_list(self, itemtype):
        raise NotImplementedError("implement me")
