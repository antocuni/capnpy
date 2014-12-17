import capnpy
from capnpy.ptr import StructPtr, ListPtr
from capnpy.blob import Blob


class Struct(Blob):
    """
    Abstract base class: a blob representing a struct.

    subclasses of Struct needs to provide two attributes: __data_size__ and
    __ptrs_size__; there are two alternatives:

    1) you put the as class attributes in your subclass

    2) you use GenericStruct, where they are instance attributes (and thus
       less space-efficient, but it's handy if you need to walk the buffer
       without knowing the schema
    """

    def _ptr_by_index(self, i):
        offset = (self.__data_size__ + i) * 8
        return offset, self._read_ptr(offset)

    def _get_body_range(self):
        return self._get_body_start(), self._get_body_end()

    def _get_extra_range(self):
        return self._get_extra_start(), self._get_extra_end()

    def _get_body_start(self):
        return self._offset

    def _get_body_end(self):
        return self._offset + (self.__data_size__ + self.__ptrs_size__) * 8

    def _get_extra_start(self):
        if self.__ptrs_size__ == 0:
            return self._get_body_end()
        ptr_offset, ptr = self._ptr_by_index(0)
        return self._offset + ptr.deref(ptr_offset)

    def _get_extra_end(self):
        # see doc/normalize.rst for an explanation of why we can compute the
        # extra range this way
        if self.__ptrs_size__ == 0:
            return self._get_body_end()
        ptr_offset, ptr = self._ptr_by_index(self.__ptrs_size__ - 1)
        ptr = ptr.specialize()
        blob_offet = ptr.deref(ptr_offset)
        if ptr.kind == StructPtr.KIND:
            mystruct = GenericStruct.from_buffer_and_size(self._buf,
                                                          self._offset+blob_offet,
                                                          ptr.data_size, ptr.ptrs_size)
            return mystruct._get_extra_end()
        elif ptr.kind == ListPtr.KIND:
            mylist = capnpy.list.List.from_buffer(self._buf, self._offset+blob_offet,
                                                  ptr.size_tag, ptr.item_count, Blob)
            return mylist._get_body_end()
        else:
            assert False


class GenericStruct(Struct):

    @classmethod
    def from_buffer_and_size(cls, buf, offset, data_size, ptrs_size):
        self = cls.from_buffer(buf, offset)
        self.__data_size__ = data_size
        self.__ptrs_size__ = ptrs_size
        return self

