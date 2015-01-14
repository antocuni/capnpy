import sys
from capnpy.util import extend
schema = sys.modules['capnpy.schema']

@extend(schema.Type)
class Type:
    
    def is_primitive(self):
        # note that bool is NOT considered primitive, i.e. it is handled
        # specially everywhere
        return schema.Type.__tag__.int8 <= self.which() <= schema.Type.__tag__.float64

    def is_builtin(self):
        return schema.Type.__tag__.void <= self.which() <= schema.Type.__tag__.data
