from capnpy.type import Types, BuiltinType
from capnpy.list import PrimitiveList, StructList, StringList
from capnpy import struct_

class Void(object):

    def __init__(self, name):
        self.name = name

    def __get__(self, blob, cls):
        if blob is None:
            return self
        return None

    def __repr__(self):
        return '<Field %s: Void>' % self.name

class Primitive(object):

    def __init__(self, name, offset, type, default_=0):
        self.name = name
        self.offset = offset
        self.type = type
        self.default_ = default_
        self.fmt = type.fmt

    def __get__(self, blob, cls):
        if blob is None:
            return self
        val = blob._read_primitive(self.offset, self.type)
        if self.default_:
            val ^= self.default_
        return val

    def __repr__(self):
        s = '<Field %s +%d: Primitive, type=%s' % (self.name, self.offset, self.type.name)
        if self.default_ == 0:
            s += '>'
        else:
            s += ', default=%s>' % self.default_
        return s

class NullablePrimitive(Primitive):

    def __init__(self, name, offset, type, default_, nullable_by):
        Primitive.__init__(self, name, offset, type, default_)
        self.nullable_by = nullable_by

    def __get__(self, blob, cls):
        if blob is None:
            return self
        isnull = self.nullable_by.__get__(blob, cls)
        if isnull:
            return None
        return Primitive.__get__(self, blob, cls)

    def __repr__(self):
        r = Primitive.__repr__(self)
        r = r[:-1] # remove the last '>'
        r += ', NULL when %s>' % self.nullable_by
        return r


class Bool(object):

    def __init__(self, name, offset, bitno, default=0):
        self.name = name
        self.offset = offset
        self.bitno = bitno
        self.bitmask = 1 << bitno
        self.default_ = default

    def __get__(self, blob, cls):
        if blob is None:
            return self
        return bool(blob._read_bit(self.offset, self.bitmask) ^ self.default_)

    def __repr__(self):
        s = '<Field %s +%d: Bool, bitno=%d' % (self.name, self.offset, self.bitno)
        if self.default_ == 0:
            s += '>'
        else:
            s += ', default=%s>' % self.default_
        return s

class String(object):

    fmt = 'q'

    def __init__(self, name, offset):
        self.name = name
        self.offset = offset

    def __get__(self, blob, cls):
        if blob is None:
            return self
        return blob._read_string(self.offset)

    def __repr__(self):
        return '<Field %s +%d: String>' % (self.name, self.offset)

class Data(object):

    fmt = 'q'

    def __init__(self, name, offset):
        self.name = name
        self.offset = offset

    def __get__(self, blob, cls):
        if blob is None:
            return self
        return blob._read_data(self.offset)

    def __repr__(self):
        return '<Field %s +%d: Data>' % (self.name, self.offset)


class List(object):

    fmt = 'q'

    def __init__(self, name, offset, item_type):
        self.name = name
        self.offset = offset
        self.item_type = item_type
        if isinstance(item_type, BuiltinType):
            if item_type.is_primitive():
                self.listcls = PrimitiveList
            elif item_type == Types.text:
                self.listcls = StringList
            else:
                raise ValueError('Unknown item type: %s' % item_type)
        elif issubclass(item_type, struct_.Struct):
            self.listcls = StructList
        else:
            raise ValueError('Unknown item type: %s' % item_type)

    def __get__(self, blob, cls):
        if blob is None:
            return self
        return blob._read_list(self.offset, self.listcls, self.item_type)

    def __repr__(self):
        return ('<Field %s +%d: List, listcls=%s, item_type=%s>' %
                (self.name, self.offset, self.listcls.__name__, self.item_type))


class Struct(object):

    fmt = 'q'

    def __init__(self, name, offset, structcls):
        self.name = name
        self.offset = offset
        self.structcls = structcls

    def __get__(self, blob, cls):
        if blob is None:
            return self
        return blob._read_struct(self.offset, self.structcls)

    def __repr__(self):
        return ('<Field %s +%d: Struct, structcls=%s>' %
                (self.name, self.offset, self.structcls.__name__))


class Enum(object):

    fmt = Types.int16.fmt

    def __init__(self, name, offset, enumcls):
        self.name = name
        self.offset = offset
        self.enumcls = enumcls

    def __get__(self, blob, cls):
        if blob is None:
            return self
        return blob._read_enum(self.offset, self.enumcls)

    def __repr__(self):
        return ('<Field %s +%d: Enum, enumcls=%s>' %
                (self.name, self.offset, self.enumcls.__name__))


class Union(object):

    def __init__(self, tag, field):
        self.tag = tag
        self.field = field

    def __get__(self, blob, cls):
        if blob is None:
            return self
        blob._ensure_union(self.tag)
        return self.field.__get__(blob, cls)

    def __repr__(self):
        return '<Union %s: %s>' % (self.tag, self.field)


class Group(object):

    def __init__(self, groupcls):
        self.groupcls = groupcls

    def __get__(self, blob, cls):
        if blob is None:
            return self
        return blob._read_group(self.groupcls)

    def __repr__(self):
        return '<Group %s>' % self.groupcls.__name__


class AnyPointer(object):

    def __init__(self, name, offset):
        self.name = name
        self.offset = offset

    def __get__(self, blob, cls):
        if blob is None:
            return self
        raise ValueError("Cannot get fields of type AnyPointer")

    def __repr__(self):
        return '<Field %s +%d: AnyPointer>' % (self.name, self.offset)
