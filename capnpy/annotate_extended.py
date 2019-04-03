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
