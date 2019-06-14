from capnpy.blob import Blob
from capnpy import ptr

class AnyPointer(object):

    def __init__(self, struct_, offset):
        self.struct_ = struct_
        self.offset = offset

    def is_struct(self):
        p = self.struct_._read_fast_ptr(self.offset)
        return ptr.kind(p) == ptr.STRUCT

    def is_list(self):
        p = self.struct_._read_fast_ptr(self.offset)
        return ptr.kind(p) == ptr.LIST

    def is_text(self):
        p = self.struct_._read_fast_ptr(self.offset)
        return (ptr.kind(p) == ptr.LIST and
                ptr.list_size_tag(p) == ptr.LIST_SIZE_8)

    # from the AnyPointer point of view, there is no difference between text
    # and data
    is_data = is_text

    def as_text(self):
        raise Exception("Use as_text_bytes or as_text_unicode as needed")

    def as_text_bytes(self):
        return self.struct_._read_text_bytes(self.offset)

    def as_text_unicode(self):
        return self.struct_._read_text_unicode(self.offset)

    def as_data(self):
        return self.struct_._read_data(self.offset)

    def as_struct(self, structcls):
        return self.struct_._read_struct(self.offset, structcls)

    def as_list(self, item_type):
        return self.struct_._read_list(self.offset, item_type)
