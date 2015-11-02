from capnpy import schema
from capnpy.type import Types
from capnpy.util import extend

@extend(schema.Field)
class Field:

    def emit(self, m, node):
        name = m._field_name(self)
        self._emit(m, node, name)
        if self.discriminantValue != Field.noDiscriminant:
            line = '{name} = __.field.Union({discriminantValue}, {name})'
            m.w(line, name=name, discriminantValue=self.discriminantValue)


@extend(schema.Field__Slot)
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
        typename = str(self.slot.type.which())
        t = getattr(Types, typename)
        size = t.calcsize()
        delta = 0
        default = m._get_value(self.slot.defaultValue)
        line = ('{name} = __.field.Primitive("{name}", {offset}, '
                                  '__.Types.{typename}, default_={default})')
        m.w(line, name=name, offset=offset, typename=typename, default=default)

    def _emit_bool(self, m, name):
        size = 0
        delta = 0
        byteoffset, bitoffset = divmod(self.slot.offset, 8)
        default = m._get_value(self.slot.defaultValue)
        m.w('{name} = __.field.Bool("{name}", {byteoffset}, {bitoffset}, {default})',
            name=name, byteoffset=byteoffset, bitoffset=bitoffset, default=default)

    def _emit_text(self, m, name, offset):
        m.w('{name} = __.field.String("{name}", {offset})', name=name, offset=offset)

    def _emit_data(self, m, name, offset):
        m.w('{name} = __.field.Data("{name}", {offset})', name=name, offset=offset)

    def _emit_struct(self, m, name, offset):
        structname = m._get_typename(self.slot.type)
        m.w('{name} = __.field.Struct("{name}", {offset}, {structname})',
            name=name, offset=offset, structname=structname)

    def _emit_list(self, m, name, offset):
        itemtype = m._get_typename(self.slot.type.list.elementType)
        m.w('{name} = __.field.List("{name}", {offset}, {itemtype})',
            name=name, offset=offset, itemtype=itemtype)
        
    def _emit_enum(self, m, name, offset):
        enumname = m._get_typename(self.slot.type)
        m.w('{name} = __.field.Enum("{name}", {offset}, {enumname})',
            name=name, offset=offset, enumname=enumname)
        
    def _emit_void(self, m, name, offset):
        m.w('{name} = __.field.Void("{name}")', name=name)
        
    def _emit_anyPointer(self, m, name, offset):
        m.w('{name} = __.field.AnyPointer("{name}", {offset})', name=name, offset=offset)


@extend(schema.Field__Group)
class Field__Group:

    def _emit(self, m, node, name):
        group = m.allnodes[self.group.typeId]
        group.emit_definition(m)
        m.w('%s = __.field.Group(%s)' % (name, m._pyname(group)))
        #
        ngroup = self.is_nullable(m)
        if ngroup:
            privname = '_' + name
            m.w()
            m.w('{privname} = {name}', privname=privname, name=name)
            m.w('@property')
            with m.code.def_(name, ['self']):
                with m.block('if self.{privname}.is_null:', privname=privname):
                    m.w('return None')
                m.w('return self.{privname}.value', privname=privname)
            m.w()
