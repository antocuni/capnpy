from capnpy import schema
from capnpy.type import Types

@schema.Field.__extend__
class Field:

    def emit(self, m, node):
        name = m._field_name(self)
        union_check_done = self._emit(m, node, name)
        if not union_check_done and self.discriminantValue != Field.noDiscriminant:
            line = '{name} = _field.Union({discriminantValue}, {name})'
            m.w(line, name=name, discriminantValue=self.discriminantValue)


@schema.Field__Slot.__extend__
class Field__Slot:

    def _emit(self, m, node, name):
        ns = m.code.new_scope()
        ns.offset = self.slot.offset * self.slot.get_size()
        if self.discriminantValue != Field.noDiscriminant:
            ns.ensure_union = 'self._ensure_union(%s)' % self.discriminantValue
        else:
            ns.ensure_union = ''
        #
        if self.slot.type.is_bool():
            return self._emit_bool(m, ns, name)
        #
        if self.slot.type.is_primitive():
            return self._emit_primitive(m, ns, name)
        elif self.slot.hadExplicitDefault:
            raise ValueError("explicit defaults not supported for field %s" % self)
        else:
            # a bit of metaprogramming: call _emit_text, _emit_struct, etc,
            # depending on the type
            #
            methname = '_emit_%s' % self.slot.type.which()
            _emit = getattr(self, methname, None)
            if _emit is None:
                raise NotImplementedError('Unknown type: %s' % self.slot.type)
            else:
                return _emit(m, ns, name)

    def _emit_void(self, m, ns, name):
        m.def_property(ns, name, """
            {ensure_union}
            return None
        """)
        return True

    def _emit_primitive(self, m, ns, name):
        ns.typename = '_Types.%s' % self.slot.type.which()
        ns.default_ = self.slot.defaultValue.as_pyobj()
        ns.ifmt = "ord(%r)" % self.slot.get_fmt()
        m.def_property(ns, name, """
            {ensure_union}
            value = self._read_data({offset}, {ifmt})
            if {default_} != 0:
                value = value ^ {default_}
            return value
        """)
        return True

    def _emit_bool(self, m, ns, name):
        byteoffset, bitoffset = divmod(self.slot.offset, 8)
        ns.offset = byteoffset
        ns.bitmask = 1 << bitoffset
        ns.default_ = self.slot.defaultValue.as_pyobj()
        m.def_property(ns, name, """
            {ensure_union}
            value = self._read_bit({offset}, {bitmask})
            if {default_} != 0:
                value = value ^ {default_}
            return value
        """)
        return True

    def _emit_enum(self, m, ns, name):
        ns.enumcls = self.slot.type.runtime_name(m)
        m.def_property(ns, name, """
            {ensure_union}
            return self._read_enum({offset}, {enumcls})
        """)

    def _emit_text(self, m, ns, name):
        ns.name = name
        m.def_property(ns, name, """
            {ensure_union}
            return self._read_str_text({offset})
        """)
        self._emit_has_method(ns)

    def _emit_data(self, m, ns, name):
        ns.name = name
        m.def_property(ns, name, """
            {ensure_union}
            return self._read_str_data({offset})
        """)
        self._emit_has_method(ns)

    def _emit_struct(self, m, ns, name):
        ns.name = name
        # XXX: in case of nested structs, using the runtime name (such as
        # Outer.Inner.Point) might be slower in pyx mode, because it has to do
        # the lookup at runtime.
        ns.structname = self.slot.type.runtime_name(m)
        m.def_property(ns, name, """
            {ensure_union}
            return self._read_struct({offset}, {structname})
        """)
        self._emit_has_method(ns)

    def _emit_list(self, m, ns, name):
        ns.name = name
        element_type = self.slot.type.list.elementType
        ns.itemtype = element_type.runtime_name(m)
        if element_type.is_primitive():
            ns.listcls = '_PrimitiveList'
        elif element_type.is_string():
            ns.listcls = '_StringList'
        elif element_type.is_struct():
            ns.listcls = '_StructList'
        else:
            raise ValueError('Unsupported: list of %s', ns.itemtype)
        #
        m.def_property(ns, name, """
            {ensure_union}
            return self._read_list({offset}, {listcls}, {itemtype})
        """)
        self._emit_has_method(ns)

    def _emit_anyPointer(self, m, ns, name):
        ns.name = name
        m.def_property(ns, name, """
            {ensure_union}
            raise ValueError("Cannot get fields of type AnyPointer")
        """)
        self._emit_has_method(ns)

    def _emit_has_method(self, ns):
        ns.ww("""
            def has_{name}(self):
                offset, ptr = self._read_ptr({offset})
                return ptr != 0
        """)
        ns.w()


@schema.Field__Group.__extend__
class Field__Group:

    def _emit(self, m, node, name):
        groupnode = m.allnodes[self.group.typeId]
        ns = m.code.new_scope()
        ns.name = name
        ns.clsname = groupnode.compile_name(m)
        if self.is_nullable(m):
            ns.privname = '_' + name
            ns.ww("""
                {privname} = _field.Group({clsname})
                @property
                def {name}(self):
                    if self.{privname}.is_null:
                        return None
                    return self.{privname}.value
            """)
        else:
            ns.w('{name} = _field.Group({clsname})')
