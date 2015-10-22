import sys
from capnpy.type import Types
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


@extend(schema.Field)
class Field:

    def is_group(self):
        return self.which() == schema.Field.__tag__.group

    def is_void(self):
        return (self.which() == schema.Field.__tag__.slot and
                self.slot.type.which() == schema.Type.__tag__.void)

    def is_primitive(self):
        return (self.which() == schema.Field.__tag__.slot and
                self.slot.type.is_primitive())

    def is_nullable(self, compiler):
        for ann in self.annotations or []:
            ann_node = compiler.allnodes[ann.id]
            if ann_node.displayName == "capnpy/py.capnp:nullable":
                assert ann.value.void is None
                return True
        return None

    def get_fmt(self):
        if self.which() == schema.Field.__tag__.slot:
            if self.slot.type.is_primitive():
                typename = str(self.slot.type.which())
                t = getattr(Types, typename)
                return t.fmt

    def get_size(self):
        if self.which() == schema.Field.__tag__.slot:
            if self.slot.type.is_primitive():
                typename = str(self.slot.type.which())
                t = getattr(Types, typename)
                return t.calcsize()

    def get_offset(self):
        return self.slot.offset * self.get_size()
