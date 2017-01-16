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
        # first of all check for nested lists, for which we do NOT support the
        # prebuilt ItemType optimization which is implemented below
        if self.is_list():
            inner_item_type = self.list.elementType.list_item_type(m)
            return '_ListItemType(%s)' % inner_item_type
        #
        compile_name = self.compile_name(m)
        if m.pyx:
            # on CPython, try to use the prebuilt ItemType when possible
            if self.is_builtin():
                return '_%s_list_item_type' % self.which()
            elif self.is_struct() or self.is_enum():
                return '_%s_list_item_type' % compile_name
            else:
                raise NotImplementedError
        else:
            if self.is_primitive():
                return '_PrimitiveItemType(_Types.%s)' % self.which()
            elif self.is_bool():
                return '_BoolItemType()'
            elif self.is_text():
                return '_TextItemType(_Types.text)'
            elif self.is_data():
                return '_TextItemType(_Types.data)'
            elif self.is_struct() or self.is_enum():
                return '_%s_list_item_type' % compile_name
            elif self.is_void():
                return '_VoidItemType()'
            else:
                raise NotImplementedError


@Value.__extend__
class Value:

    def as_pyobj(self):
        val_type = str(self.which())
        return getattr(self, val_type)

