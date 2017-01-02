from capnpy.schema import Value, Type

@Type.__extend__
class Type:

    def compile_name(self, m):
        if self.is_builtin():
            return '_Types.%s' % self.which()
        elif self.is_struct():
            node = m.allnodes[self.struct.typeId]
            return node.compile_name(m)
        elif self.is_enum():
            node = m.allnodes[self.enum.typeId]
            return node.compile_name(m)
        else:
            raise NotImplementedError

    def runtime_name(self, m):
        if self.is_builtin():
            return '_Types.%s' % self.which()
        elif self.is_struct():
            node = m.allnodes[self.struct.typeId]
            return node.runtime_name(m)
        elif self.is_enum():
            node = m.allnodes[self.enum.typeId]
            return node.runtime_name(m)
        else:
            raise NotImplementedError

    def list_item_type(self, m):
        compile_name = self.compile_name(m)
        if self.is_builtin():
            return '%s.list_item_type' % compile_name
        elif self.is_struct():
            return '_%s_list_item_type' % compile_name
        elif self.is_enum():
            XXX
        else:
            raise NotImplementedError


@Value.__extend__
class Value:

    def as_pyobj(self):
        val_type = str(self.which())
        return getattr(self, val_type)

