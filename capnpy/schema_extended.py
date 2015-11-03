import sys
from capnpy.type import Types
schema = sys.modules['capnpy.schema']

@schema.Type.__extend__
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


@schema.Field.__extend__
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

    def is_nullable(self, m):
        for ann in self.annotations or []:
            ann_node = m.allnodes[ann.id]
            if ann_node.displayName == "capnpy/py.capnp:nullable":
                assert ann.value.void is None
                return True
        return False


    @schema.Field.slot.field.groupcls.__extend__
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

        def compute_offset_inside(self, data_size):
            offset = self.offset * self.get_size()
            if self.type.is_pointer():
                offset += data_size*8
            return offset


# =============================================
# hand-written union subclasses
# =============================================
#
# As of now, the compiler is not capable of generating different subclasses
# for each union tag. In the meantime, write it by hand

class Node__Struct(schema.Node): pass
class Node__Enum(schema.Node): pass
class Node__Const(schema.Node): pass
schema.Node__Struct = Node__Struct
schema.Node__Enum = Node__Enum
schema.Node__Const = Node__Const

@schema.Node.__extend__
class Node:

    @classmethod
    def from_buffer(cls, buf, offset, segment_offsets):
        self = super(Node, cls).from_buffer(buf, offset, segment_offsets)
        if self.which() == Node.__tag__.struct:
            self.__class__ = Node__Struct
        elif self.which() == Node.__tag__.enum:
            self.__class__ = Node__Enum
        elif self.which() == Node.__tag__.const:
            self.__class__ = Node__Const
        return self



class Field__Slot(schema.Field): pass
class Field__Group(schema.Field): pass
schema.Field__Slot = Field__Slot
schema.Field__Group = Field__Group

@schema.Field.__extend__
class Field:

    @classmethod
    def from_buffer(cls, buf, offset, segment_offsets):
        self = super(Field, cls).from_buffer(buf, offset, segment_offsets)
        if self.which() == Field.__tag__.slot:
            self.__class__ = Field__Slot
        elif self.which() == Field.__tag__.group:
            self.__class__ = Field__Group
        return self


# =============================================
# hand-written constructors
# =============================================
#
# As of now, the compiler is not capable of generating proper constructors for
# Type and Field, but we need them in tests and in structor.py. In the
# meantime, we write limited versions of them by hand.
import struct
from capnpy.builder import StructBuilder

@schema.Type.__extend__
class Type:

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


@schema.Field.__extend__
class Field:

    @classmethod
    def new_slot(cls, name, offset, type):
        """
        This is a very limited version of new_slot. Once we have full support for
        constructor, its signature will be more complex.
        """
        fmt = (
            # data
            'H' # [0:16]    codeOrder
            'H' # [16:32]   discriminantValue
            'I' # [32:64]   slot.offset
            'h' # [64:80]   __tag__
            'h' # [80:96]   ordinal.__tag__
            'h' # [96:112]  ordinal.explicit
            'h' # [112:128] padding
            'Q' # [128:192] group.typeId
            #
            # pointers
            'q' # [0]       name
            'q' # [1]       annotations
            'q' # [2]       slot.type
            'q' # [3]       slot.defaultValue
            )
        size = struct.calcsize(fmt)
        assert size == (cls.__data_size__ + cls.__ptrs_size__)*8
        builder = StructBuilder(fmt)
        #
        codeOrder = 0
        discriminantValue = 65535
        slot_offset = offset
        tag = cls.__tag__.slot
        ordinal_tag = 0
        ordinal_explicit = 0
        padding = 0
        group_typeId = 0
        ptr_name = builder.alloc_string(24, name)
        ptr_annotations = 0
        ptr_slot_type = builder.alloc_struct(40, schema.Type, type)
        ptr_slot_defaultValue = 0
        #
        buf = builder.build(codeOrder, discriminantValue, slot_offset,
                            tag, ordinal_tag, ordinal_explicit, padding,
                            group_typeId, ptr_name, ptr_annotations,
                            ptr_slot_type, ptr_slot_defaultValue)
        return cls.from_buffer(buf, 0, None)
