class BaseEnum(int):

    __slots__ = ()
    
    def __new__(cls, value):
        return int.__new__(cls, value)

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


def enum(name, members):
    class Enum(BaseEnum):
        __slots__ = ()
        __members__ = tuple(members)

    Enum.__name__ = name
    for i, member in enumerate(members):
        value = Enum(i)
        setattr(Enum, member, value)

    return Enum
