from capnpy.util import extend
from capnpy.enum import BaseEnum

@extend(nullable)
class nullable:

    def check(self, m):
        field = self.target
        assert field.is_group()
        name = m.py_field_name(field)
        def error(msg):
            raise ValueError('%s: %s' % (name, msg))
        #
        group = field.group.get_node(m)
        if len(group.struct.fields) != 2:
            error()
        f_is_null, f_value = group.struct.fields
        if (f_is_null.name != b'isNull' or
            f_value.name != b'value'):
            error('nullable groups must have exactly two fields: '
                  '"isNull" and "value"')
        if f_value.is_pointer():
            error('cannot use pointer types for nullable values. '
                  'Pointers are already nullable.')
        return name, f_is_null, f_value


@extend(group)
class group:

    def check(self, m):
        field = self.target
        assert field.is_void()


@extend(BoolOption)
class BoolOption:

    def __bool__(self):
        if self == BoolOption.notset:
            raise ValueError("Cannot get the truth value of a 'notset'")
        return bool(int(self))
    __nonzero__ = __bool__ # for Python2.7


@extend(TextType)
class TextType:

    @classmethod
    def parse(cls, s):
        if s == 'bytes':
            return cls.bytes
        elif s == 'unicode':
            return cls.unicode
        else:
            raise ValueError('Unknown TextType: %s' % s)


@Options.__extend__
class Options:

    FIELDS = ('version_check', 'convert_case', 'text_type', 'include_reflection_data')

    @classmethod
    def from_dict(cls, d):
        """
        Create an Options instance from the given dict.

        Each option is expressed as either a normal bool or a string; strings
        are parsed (e.g. "bytes" becomes TextType.bytes)
        """
        kwargs = {}
        for key, value in d.items():
            if key in ('version_check', 'convert_case', 'include_reflection_data'):
                kwargs[key] = value
            elif key == 'text_type':
                kwargs[key] = TextType.parse(value)
            else:
                raise ValueError("Unknown option: %s" % key)
        return cls(**kwargs)

    def combine(self, other):
        """
        Combine the options of ``self`` and ``other``. ``other``'s options take
        the precedence, if they are set.
        """
        values = {}
        for fname in self.FIELDS:
            values[fname] = getattr(self, fname)
            otherval = getattr(other, fname)
            enumcls = otherval.__class__
            assert issubclass(enumcls, BaseEnum), 'Only Enums supported for now'
            assert hasattr(enumcls, 'notset'), 'An Option enum must have a "notset" field'
            if otherval != enumcls.notset:
                values[fname] = otherval
        return self.__class__(**values)
