import sys
from capnpy.util import extend
schema = sys.modules['capnpy.schema']

@extend(schema.Type)
class Type:
    FORMAT = [None] * 12
    FORMAT[schema.Type.__tag__.int8]    = 'b'
    FORMAT[schema.Type.__tag__.uint8]   = 'B'
    FORMAT[schema.Type.__tag__.int16]   = 'h'
    FORMAT[schema.Type.__tag__.uint16]  = 'H'
    FORMAT[schema.Type.__tag__.int32]   = 'i'
    FORMAT[schema.Type.__tag__.uint32]  = 'I'
    FORMAT[schema.Type.__tag__.int64]   = 'q'
    FORMAT[schema.Type.__tag__.uint64]  = 'Q'
    FORMAT[schema.Type.__tag__.float32] = 'f'
    FORMAT[schema.Type.__tag__.float64] = 'd'
    FORMAT = tuple(FORMAT)

    def is_primitive(self):
        # note that bool is NOT considered primitive, i.e. it is handled
        # specially everywhere
        return schema.Type.__tag__.int8 <= self <= schema.Type.__tag__.float64

    def calcsize(self):
        return struct.calcsize(self.get_format())

    def get_format(self):
        return schema.Type.FORMAT[self]
