from capnpy.type import Types as _Types
from capnpy import annotate

@Type.__extend__
class Type:

    def as_type(self):
        """
        Convert between schema.Type to capnpy.type.Types.*
        We should unify the twos eventually
        """
        typename = str(self.which())
        return getattr(_Types, typename)

    def is_primitive(self):
        # note that bool is NOT considered primitive, i.e. it is handled
        # specially everywhere
        return Type.__tag__.int8 <= self.which() <= Type.__tag__.float64

    def is_builtin(self):
        return Type.__tag__.void <= self.which() <= Type.__tag__.data

    def is_pointer(self):
        return self.which() in (Type.__tag__.text,
                                Type.__tag__.data,
                                Type.__tag__.struct,
                                Type.__tag__.list,
                                Type.__tag__.anyPointer)

    def __repr__(self):
        return '<Type: %s>' % self.which()

@Node.__extend__
class Node:

    def __hash__(self):
        return hash(self.id)

    def _equals(self, other):
        return self.id == other.id


@Field.__extend__
class Field:

    def __key(self):
        # XXX: this is not strictly correct, because two fields might differ
        # for other attributes. However, the pair (name, codeOrder) should be
        # enough to uniquiely identify a field inside the parent struct, which
        # is enough for what we need (in particular, in structor.py)
        return self.name, self.codeOrder

    def __hash__(self):
        return hash(self.__key())

    def __repr__(self):
        if self.is_slot():
            return "<Field '%s': %s>" % (self.name, self.slot.type.which())
        else:
            return "<Field '%s': %s>" % (self.name, self.which())

    def _equals(self, other):
        return self.__key() == other.__key()

    def is_primitive(self):
        return (self.which() == Field.__tag__.slot and
                self.slot.type.is_primitive())

    def is_void(self):
        return (self.which() == Field.__tag__.slot and
                self.slot.type.is_void())

    def is_float32(self):
        return (self.which() == Field.__tag__.slot and
                self.slot.type.is_float32())

    def is_float64(self):
        return (self.which() == Field.__tag__.slot and
                self.slot.type.is_float64())

    def is_bool(self):
        return (self.which() == Field.__tag__.slot and
                self.slot.type.is_bool())

    def is_enum(self):
        return (self.which() == Field.__tag__.slot and
                self.slot.type.is_enum())

    def is_pointer(self):
        return (self.which() == Field.__tag__.slot and
                self.slot.type.is_pointer())

    def is_text(self):
        return (self.which() == Field.__tag__.slot and
                self.slot.type.is_text())

    def is_data(self):
        return (self.which() == Field.__tag__.slot and
                self.slot.type.is_data())

    def is_struct(self):
        return (self.which() == Field.__tag__.slot and
                self.slot.type.is_struct())

    def is_list(self):
        return (self.which() == Field.__tag__.slot and
                self.slot.type.which() == Type.__tag__.list)

    def is_nullable(self, m):
        return m.has_annotation(self, annotate.nullable)

    def is_part_of_union(self):
        return self.discriminantValue != Field.noDiscriminant

@Field_slot.__extend__
class Field_slot:
    def get_fmt(self):
        # XXX: this method is very hackish, we absolutely need to find a
        # cleaner way than the forest of ifs
        if self.type.is_primitive():
            return self.type.as_type().fmt
        elif self.type.is_pointer():
            return 'q'
        elif self.type.is_enum():
            return 'h'

    def get_typename(self):
        if self.type.is_primitive():
            return str(self.type.which())
        elif self.type.is_pointer():
            return 'int64'
        elif self.type.is_enum():
            return 'int16'

    def get_size(self):
        # XXX: even more hackish, we need a better way
        if self.type.is_void():
            return 0
        elif self.type.is_bool():
            # not strictly correct, but we cannot return 1/8
            return 0
        import struct
        return struct.calcsize(self.get_fmt())


# =============================================
# hand-written union subclasses
# =============================================
#
# As of now, the compiler is not capable of generating different subclasses
# for each union tag. In the meantime, write it by hand

class Node__Struct(Node): pass
class Node__Enum(Node): pass
class Node__Const(Node): pass
class Node__Annotation(Node): pass

@Node.__extend__
class Node:

    @classmethod
    def from_buffer(cls, buf, offset, data_size, ptrs_size):
        self = super(Node, cls).from_buffer(buf, offset, data_size, ptrs_size)
        if self.which() == Node.__tag__.struct:
            self.__class__ = Node__Struct
        elif self.which() == Node.__tag__.enum:
            self.__class__ = Node__Enum
        elif self.which() == Node.__tag__.const:
            self.__class__ = Node__Const
        elif self.which() == Node.__tag__.annotation:
            self.__class__ = Node__Annotation
        return self


@Node_struct.__extend__
class Node_struct:

    def is_union(self):
        return self.discriminantCount > 0

class Field__Slot(Field): pass
class Field__Group(Field): pass


@Field.__extend__
class Field:

    @classmethod
    def from_buffer(cls, buf, offset, data_size, ptrs_size):
        self = super(Field, cls).from_buffer(buf, offset, data_size, ptrs_size)
        if self.which() == Field.__tag__.slot:
            self.__class__ = Field__Slot
        elif self.which() == Field.__tag__.group:
            self.__class__ = Field__Group
        return self

