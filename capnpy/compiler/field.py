from capnpy import schema
from capnpy.type import Types

@schema.Field.__extend__
class Field:

    def emit(self, m, node):
        name = m._field_name(self)
        self._emit(m, node, name)
        if self.discriminantValue != Field.noDiscriminant:
            line = '{name} = _field.Union({discriminantValue}, {name})'
            m.w(line, name=name, discriminantValue=self.discriminantValue)


@schema.Field__Slot.__extend__
class Field__Slot:

    def _emit(self, m, node, name):
        if self.slot.type.is_bool():
            self._emit_bool(m, name)
            return
        #
        offset = self.slot.compute_offset_inside(node.struct.dataWordCount)
        if self.slot.type.is_primitive():
            self._emit_primitive(m, name, offset)
        else:
            # a bit of metaprogramming: call _emit_text, _emit_struct, etc,
            # depending on the type
            methname = '_emit_%s' % self.slot.type.which()
            _emit = getattr(self, methname, None)
            if _emit is None:
                raise NotImplementedError('Unknown type: %s' % self.slot.type)
            else:
                _emit(m, name, offset)
            #
            if self.slot.hadExplicitDefault:
                raise ValueError("explicit defaults not supported for field %s" % self)


    def _emit_primitive(self, m, name, offset):
        if m.pyx:
            with m.block('property {name}:', name=name):
                with m.block('def __get__(self):'):
                    default_ = self.slot.defaultValue.as_pyobj()
                    m.w('value = _upf("{fmt}", self._buf, self._offset+{offset})',
                        fmt=self.slot.get_fmt(), offset=offset)
                    m.w('value = value ^ {default_}', default_=default_)
                    m.w('return value')
        else:
            typename = str(self.slot.type.which())
            default = self.slot.defaultValue.as_pyobj()
            line = ('{name} = _field.Primitive("{name}", {offset}, '
                                      '_Types.{typename}, default_={default})')
            m.w(line, name=name, offset=offset, typename=typename, default=default)

    def _emit_bool(self, m, name):
        byteoffset, bitoffset = divmod(self.slot.offset, 8)
        default = self.slot.defaultValue.as_pyobj()
        m.w('{name} = _field.Bool("{name}", {byteoffset}, {bitoffset}, {default})',
            name=name, byteoffset=byteoffset, bitoffset=bitoffset, default=default)

    def _emit_text(self, m, name, offset):
        m.w('{name} = _field.String("{name}", {offset})', name=name, offset=offset)

    def _emit_data(self, m, name, offset):
        m.w('{name} = _field.Data("{name}", {offset})', name=name, offset=offset)

    def _emit_struct(self, m, name, offset):
        structname = m._get_typename(self.slot.type, 'compile')
        m.w('{name} = _field.Struct("{name}", {offset}, {structname})',
            name=name, offset=offset, structname=structname)

    def _emit_list(self, m, name, offset):
        itemtype = m._get_typename(self.slot.type.list.elementType, 'compile')
        m.w('{name} = _field.List("{name}", {offset}, {itemtype})',
            name=name, offset=offset, itemtype=itemtype)
        
    def _emit_enum(self, m, name, offset):
        enumname = m._get_typename(self.slot.type, 'compile')
        m.w('{name} = _field.Enum("{name}", {offset}, {enumname})',
            name=name, offset=offset, enumname=enumname)
        
    def _emit_void(self, m, name, offset):
        m.w('{name} = _field.Void("{name}")', name=name)
        
    def _emit_anyPointer(self, m, name, offset):
        m.w('{name} = _field.AnyPointer("{name}", {offset})', name=name, offset=offset)


@schema.Field__Group.__extend__
class Field__Group:

    def _emit(self, m, node, name):
        groupnode = m.allnodes[self.group.typeId]
        clsname = groupnode.compile_name(m)
        if self.is_nullable(m):
            privname = '_' + name
            m.w('{privname} = _field.Group({clsname})', privname=privname, clsname=clsname)
            m.w('@property')
            with m.code.def_(name, ['self']):
                with m.block('if self.{privname}.is_null:', privname=privname):
                    m.w('return None')
                m.w('return self.{privname}.value', privname=privname)
            m.w()
        else:
            m.w('{name} = _field.Group({clsname})', name=name, clsname=clsname)
