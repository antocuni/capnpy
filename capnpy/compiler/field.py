from capnpy import schema
from capnpy import annotate
from capnpy.type import Types
from capnpy.compiler.fieldtree import FieldTree
from capnpy import annotate

@schema.Field.__extend__
class Field:

    def compute_options(self, m, parent_opt):
        m.compute_options_generic(self, parent_opt)

    def emit(self, m, node):
        name = m.py_field_name(self)
        ns = m.code.new_scope()
        if self.is_part_of_union():
            ns.ensure_union = 'self._ensure_union(%s)' % self.discriminantValue
        else:
            ns.ensure_union = '# no union check'
        self._emit(m, ns, name)


@schema.Field__Slot.__extend__
class Field__Slot:

    def _emit(self, m, ns, name):
        if self.slot.hadExplicitDefault:
            if not (self.slot.type.is_primitive() or
                    self.slot.type.is_enum() or
                    self.slot.type.is_bool()):
                raise ValueError("explicit defaults not supported for field %s" % self)

        ns.offset = self.slot.offset * self.slot.get_size()
        #
        if self.slot.type.is_void():
            self._emit_void(m, ns, name)
        elif self.slot.type.is_float32() or self.slot.type.is_float64():
            self._emit_float(m, ns, name)
        elif self.slot.type.is_primitive():
            self._emit_primitive(m, ns, name)
        elif self.slot.type.is_bool():
            return self._emit_bool(m, ns, name)
        elif self.slot.type.is_enum():
            return self._emit_enum(m, ns, name)
        elif self.is_text_bytes(m):
            return self._emit_text_bytes(m, ns, name)
        elif self.is_text_unicode(m):
            return self._emit_text_unicode(m, ns, name)
        elif self.slot.type.is_data():
            return self._emit_data(m, ns, name)
        elif self.slot.type.is_struct():
            return self._emit_struct(m, ns, name)
        elif self.slot.type.is_list():
            return self._emit_list(m, ns, name)
        elif self.slot.type.is_anyPointer():
            return self._emit_anyPointer(m, ns, name)
        else:
            raise NotImplementedError('Unknown type: %s' %
                                      self.slot.type.runtime_name(m))

    def _emit_void(self, m, ns, name):
        field = m.field_override.get(self.id, None)
        if field:
            field._emit(m, ns, name)
        else:
            m.def_property(ns, name, """
                {ensure_union}
                return None
            """)

    def _emit_primitive(self, m, ns, name):
        ns.typename = '_Types.%s' % self.slot.type.which()
        ns.default_ = self.slot.defaultValue.as_pyobj()
        ns.ifmt = "ord(%r)" % self.slot.get_fmt()
        m.def_property(ns, name, """
            {ensure_union}
            value = self._read_primitive({offset}, {ifmt})
            if {default_} != 0:
                value = value ^ {default_}
            return value
        """)

    def _emit_float(self, m, ns, name):
        ns.typename = '_Types.%s' % self.slot.type.which()
        ns.default_ = self.slot.defaultValue.as_pyobj()
        ns.ifmt = "ord(%r)" % self.slot.get_fmt()
        m.def_property(ns, name, """
            {ensure_union}
            value = self._read_primitive({offset}, {ifmt})

            if {default_} != 0:
                value = _fxor(value, {default_}, {ifmt})
            return value
        """)

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

    def _emit_enum(self, m, ns, name):
        ns.enumcls = self.slot.type.compile_name(m)
        ns.default_ = self.slot.defaultValue.as_pyobj()
        ns.newf = '_new'
        m.def_property(ns, name, """
            {ensure_union}
            value = self._read_int16({offset})
            if {default_} != 0:
                value = (value ^ {default_})
            return {enumcls}.{newf}(value)
        """)

    def _emit_text_bytes(self, m, ns, name):
        ns.name = name
        m.def_property(ns, name, """
            {ensure_union}
            return self._read_text_bytes({offset})
        """)
        ns.ww("""
            {cpdef} get_{name}(self):
                return self._read_text_bytes({offset}, default_=b"")
        """)
        ns.w()
        self._emit_has_method(ns)

    def _emit_text_unicode(self, m, ns, name):
        ns.name = name
        m.def_property(ns, name, """
            {ensure_union}
            return self._read_text_unicode({offset})
        """)
        ns.ww("""
            {cpdef} get_{name}(self):
                return self._read_text_unicode({offset}, default_=b"")
        """)
        ns.w()
        self._emit_has_method(ns)

    def _emit_data(self, m, ns, name):
        ns.name = name
        m.def_property(ns, name, """
            {ensure_union}
            return self._read_data({offset})
        """)
        ns.ww("""
            {cpdef} get_{name}(self):
                return self._read_data({offset}, default_=b"")
        """)
        ns.w()
        self._emit_has_method(ns)

    def _emit_struct(self, m, ns, name):
        ns.name = name
        # XXX: in case of nested structs, using the runtime name (such as
        # Outer.Inner.Point) might be slower in pyx mode, because it has to do
        # the lookup at runtime.
        ns.structcls = self.slot.type.runtime_name(m)
        if m.pyx:
            ns.cdef_offset = 'cdef long offset'
            ns.cdef_p = 'cdef long p'
            ns.cdef_obj = 'cdef _Struct obj'
        else:
            ns.cdef_offset = 'offset'
            ns.cdef_p = 'p'
            ns.cdef_obj = 'obj'
        m.def_property(ns, name, """
            {ensure_union}
            {cdef_offset} = {offset}
            {cdef_p} = self._read_fast_ptr(offset)
            if _ptr.kind(p) == _ptr.FAR:
                offset, p = self._read_far_ptr(offset)
            else:
                offset += self._ptrs_offset
            if p == 0:
                return None
            {cdef_obj} = {structcls}.__new__({structcls})
            obj._init_from_pointer(self._seg, offset, p)
            return obj
        """)
        ns.ww("""
            {cpdef} get_{name}(self):
                res = self.{name}
                if res is None:
                    return {structcls}.from_buffer(b'', 0, data_size=0, ptrs_size=0)
                return res
        """)
        ns.w()
        self._emit_has_method(ns)

    def _emit_list(self, m, ns, name):
        options = m.options(self)
        ns.name = name
        t = self.slot.type.list.elementType
        ns.list_item_type = t.list_item_type(m, options)
        m.def_property(ns, name, """
            {ensure_union}
            return self._read_list({offset}, {list_item_type})
        """)
        ns.ww("""
            {cpdef} get_{name}(self):
                res = self.{name}
                if res is None:
                    return _List.from_buffer(b'', 0, 0, 0, {list_item_type})
                return res
        """)
        ns.w()
        self._emit_has_method(ns)

    def _emit_anyPointer(self, m, ns, name):
        ns.name = name
        m.def_property(ns, name, """
            {ensure_union}
            if not self.has_{name}():
                return None
            return _AnyPointer(self, {offset})
        """)
        self._emit_has_method(ns)

    def _emit_has_method(self, ns):
        ns.ww("""
            {cpdef} has_{name}(self):
                ptr = self._read_fast_ptr({offset})
                return ptr != 0
        """)
        ns.w()


@schema.Field__Group.__extend__
class Field__Group:

    def _emit(self, m, ns, name):
        groupnode = self.group.get_node(m)
        ns.groupcls = groupnode.compile_name(m)
        ns.name = name
        nullable = self.is_nullable(m)
        if nullable:
            nullable.check(m)
            ns.privname = '_' + name
            m.def_property(ns, name, """
                g = self.{privname}
                if g.is_null:
                    return None
                return g.value
            """)
            name = ns.privname
        #
        m.def_property(ns, name, """
            {ensure_union}
            obj = {groupcls}.__new__({groupcls})
            _Struct._init_from_buffer(obj, self._seg, self._data_offset,
                                      self._data_size, self._ptrs_size)
            return obj
        """)
        #
        if not nullable:
            # these are emitted only for non-nullable groups
            self._emit_ctor_like(m, ns, name)


    def _emit_ctor_like(self, m, ns, name):
        ## emit something like this:
        ## @staticmethod
        ## def Position(x=0, y=42):
        ##     return x, y
        ##
        groupnode = self.group.get_node(m)
        union_default = None
        if groupnode.struct.is_union():
            union_default = '_undefined'
        tree = FieldTree(m, groupnode)
        argnames, params = tree.get_args_and_params()
        #
        ns.argnames = m.code.args(argnames)
        ns.params = m.code.params(params)
        ns.capitalname = ns.name.capitalize()
        ns.ww("""
            @staticmethod
            def {capitalname}({params}):
                return {argnames},
        """)
        ns.w()


@schema.Field_group.__extend__
class Field_group:
    def get_node(self, m):
        return m.allnodes[self.typeId]
