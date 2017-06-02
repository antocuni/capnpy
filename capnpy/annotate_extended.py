from capnpy.util import extend

@extend(nullable)
class nullable:

    def check(self, m):
        field = self.target
        assert field.is_group()
        name = m._field_name(field)
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

    def __nonzero__(self):
        if self == BoolOption.notset:
            raise ValueError("Cannot get the truth value of a 'notset'")
        return bool(int(self))

@Options.__extend__
class Options:

    FIELDS = ('convert_case',)

    def combine(self, other):
        """
        Combine the options of ``self`` and ``other``. ``other``'s options take
        the precedence, if they are set.
        """
        values = {}
        for fname in self.FIELDS:
            values[fname] = getattr(self, fname)
            otherval = getattr(other, fname)
            assert isinstance(otherval, BoolOption), 'Only BoolOption supported for now'
            if otherval != BoolOption.notset:
                values[fname] = otherval
            return self.__class__(**values)
