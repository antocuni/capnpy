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

    def is_bool(self):
        return self.which() == schema.Type.__tag__.bool

    def is_enum(self):
        return self.which() == schema.Type.__tag__.enum

    def is_pointer(self):
        return self.which() in (schema.Type.__tag__.text,
                                schema.Type.__tag__.data,
                                schema.Type.__tag__.struct,
                                schema.Type.__tag__.list,
                                schema.Type.__tag__.anyPointer)


@extend(schema.Field)
class Field:

    def is_slot(self):
        return self.which() == schema.Field.__tag__.slot

    def is_group(self):
        return self.which() == schema.Field.__tag__.group

    def is_void(self):
        return (self.which() == schema.Field.__tag__.slot and
                self.slot.type.which() == schema.Type.__tag__.void)

    def is_primitive(self):
        return (self.which() == schema.Field.__tag__.slot and
                self.slot.type.is_primitive())

    def is_pointer(self):
        return (self.which() == schema.Field.__tag__.slot and
                self.slot.type.is_pointer())

    def is_string(self):
        return (self.which() == schema.Field.__tag__.slot and
                self.slot.type.which() == schema.Type.__tag__.text)

    def is_struct(self):
        return (self.which() == schema.Field.__tag__.slot and
                self.slot.type.which() == schema.Type.__tag__.struct)

    def is_list(self):
        return (self.which() == schema.Field.__tag__.slot and
                self.slot.type.which() == schema.Type.__tag__.list)

    def is_nullable(self, compiler):
        for ann in self.annotations or []:
            ann_node = compiler.allnodes[ann.id]
            if ann_node.displayName == "capnpy/py.capnp:nullable":
                assert ann.value.void is None
                return True
        return None


    @extend(schema.Field.slot.field.groupcls)
    class _:
        def get_fmt(self):
            # XXX: this method is very hackish, we absolutely need to find a
            # cleaner way than the forest of ifs
            if self.type.is_primitive():
                typename = str(self.type.which())
                t = getattr(Types, typename)
                return t.fmt
            elif self.type.is_pointer():
                return 'q'
            elif self.type.is_enum():
                return 'h'

        def get_size(self):
            # XXX: even more hackish, we need a better way
            import struct
            return struct.calcsize(self.get_fmt())

        def get_offset(self, data_size):
            offset = self.offset * self.get_size()
            if self.type.is_pointer():
                offset += data_size*8
            return offset
