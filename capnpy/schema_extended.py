import sys
from capnpy.type import Types
from capnpy.util import extend
schema = sys.modules['capnpy.schema']

@extend(schema.Type)
class Type:

    def as_type(self):
        """
        Convert between schema.Type to capnpy.type.Types.*
        We should unify the twos eventually
        """
        typename = str(self.which())
        return getattr(Types, typename)

    def is_primitive(self):
        # note that bool is NOT considered primitive, i.e. it is handled
        # specially everywhere
        return schema.Type.__tag__.int8 <= self.which() <= schema.Type.__tag__.float64

    def is_builtin(self):
        return schema.Type.__tag__.void <= self.which() <= schema.Type.__tag__.data

    def is_bool(self):
        return self.which() == schema.Type.__tag__.bool

    def is_void(self):
        return self.which() == schema.Type.__tag__.void

    def is_enum(self):
        return self.which() == schema.Type.__tag__.enum

    def is_string(self):
        return self.which() == schema.Type.__tag__.text

    def is_struct(self):
        return self.which() == schema.Type.__tag__.struct

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
                self.slot.type.is_void())

    def is_primitive(self):
        return (self.which() == schema.Field.__tag__.slot and
                self.slot.type.is_primitive())

    def is_pointer(self):
        return (self.which() == schema.Field.__tag__.slot and
                self.slot.type.is_pointer())

    def is_string(self):
        return (self.which() == schema.Field.__tag__.slot and
                self.slot.type.is_string())


    def is_struct(self):
        return (self.which() == schema.Field.__tag__.slot and
                self.slot.type.is_struct())

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
                return self.type.as_type().fmt
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


# =============================================
# hand-written constructors
# =============================================
#
# As of now, the compiler is not capable of generating proper constructors for
# Type and Field, but we need them in tests and in structor.py. In the
# meantime, we write limited versions of them by hand.
import struct

@extend(schema.Type)
class Type:
    # Type instances are 32 bytes (3 words of data + 1 word of pointers).
    # We support constructors for primitive fields only, so the only fields we
    ## data_size = 3
    ## ptrs_size = 1

    @classmethod
    def __new_primitive(cls, tag):
        assert 0 <= tag <= 13, 'non-primitive types non supported'
        assert cls.__tag_offset__ == 0 # the tag is the first 16 bits
        assert cls.__data_size__ + cls.__ptrs_size__ == 4 # 32 bytes in total
        fmt = 'h' + 'x'*30
        assert struct.calcsize(fmt) == 32
        buf = struct.pack(fmt, tag)
        return cls.from_buffer(buf, 0, None)

    new_void = classmethod(lambda cls: cls.__new_primitive(0))
    new_bool = classmethod(lambda cls: cls.__new_primitive(1))
    new_int8 = classmethod(lambda cls: cls.__new_primitive(2))
    new_int16 = classmethod(lambda cls: cls.__new_primitive(3))
    new_int32 = classmethod(lambda cls: cls.__new_primitive(4))
    new_int64 = classmethod(lambda cls: cls.__new_primitive(5))
    new_uint8 = classmethod(lambda cls: cls.__new_primitive(6))
    new_uint16 = classmethod(lambda cls: cls.__new_primitive(7))
    new_uint32 = classmethod(lambda cls: cls.__new_primitive(8))
    new_uint64 = classmethod(lambda cls: cls.__new_primitive(9))
    new_float32 = classmethod(lambda cls: cls.__new_primitive(10))
    new_float64 = classmethod(lambda cls: cls.__new_primitive(11))
    new_text = classmethod(lambda cls: cls.__new_primitive(12))
    new_data = classmethod(lambda cls: cls.__new_primitive(13))
