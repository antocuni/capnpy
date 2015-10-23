class NullableGroup(object):

    def __init__(self, compiler, field):
        assert field.is_group()
        self.name = compiler._field_name(field)
        self.is_null, self.value = self._unpack_field(compiler, field)
        self.is_null_name = '_%s_is_null' % self.name

    def _unpack_field(self, compiler, field):
        group = compiler.allnodes[field.group.typeId]
        if len(group.struct.fields) != 2:
            self._error()
        is_null, value = group.struct.fields
        if is_null.name != 'isNull':
            self._error()
        if value.name != 'value':
            self._error()
        return is_null, value

    def _error(self):
        msg = '%s: nullable groups must have exactly two fields: "isNull" and "value"'
        raise ValueError(msg % self.name)
