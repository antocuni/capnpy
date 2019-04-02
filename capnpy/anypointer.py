from capnpy.blob import Blob

class AnyPointer(object):

    def __init__(self, struct_, offset):
        self.struct_ = struct_
        self.offset = offset

    def as_text(self):
        return self.struct_._read_str_text(self.offset)

