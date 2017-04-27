from capnpy.util import magic_setattr

class BaseEnum(int):
    __slots__ = ()
    __members__ = ()

    @property
    def name(self):
        try:
            return self.__members__[self]
        except IndexError:
            return 'unknown<%d>' % self

    def __repr__(self):
        return '<%s.%s: %d>' % (self.__class__.__name__, self.name, self)

    def __str__(self):
        return self.name

def fill_enum(cls):
    for i, member in enumerate(cls.__members__):
        value = cls(i)
        magic_setattr(cls, member, value)

def enum(name, members):
    """
    Create a new Enum type dynamically. Mostly used by tests
    """
    class Enum(BaseEnum):
        __slots__ = ()
        __members__ = tuple(members)
    Enum.__name__ = name
    fill_enum(Enum)
    return Enum
