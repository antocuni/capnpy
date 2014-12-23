class BaseEnum(int):
    
    def __new__(cls, value):
        if not 0 <= value < len(cls.__members__):
            raise ValueError, 'Unkown %s value: %d' % (cls.__name__, value)
        return int.__new__(cls, value)

    @property
    def name(self):
        return self.__members__[self]

    def __repr__(self):
        return '<%s.%s: %d>' % (self.__class__.__name__, self.name, self)

    def __str__(self):
        return '%s.%s' % (self.__class__.__name__, self.name)


def enum(name, members):
    class Enum(BaseEnum):
        __members__ = tuple(members)

    Enum.__name__ = name
    for i, member in enumerate(members):
        value = Enum(i)
        setattr(Enum, member, value)

    return Enum
