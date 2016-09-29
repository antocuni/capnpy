from capnpy.util import extend

@extend(nullable)
class nullable:

    def check(self, m):
        field = self.target
        assert field.is_group()
        name = m._field_name(field)
        def error():
            msg = '%s: nullable groups must have exactly two fields: "isNull" and "value"'
            raise ValueError(msg % name)
        #
        group = m.allnodes[field.group.typeId]
        if len(group.struct.fields) != 2:
            error()
        f_is_null, f_value = group.struct.fields
        if f_is_null.name != 'isNull':
            error()
        if f_value.name != 'value':
            error()
        return name, f_is_null, f_value

