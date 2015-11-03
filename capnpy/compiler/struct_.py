from capnpy import schema
from capnpy.compiler.structor import Structor


@schema.Node__Struct.__extend__
class Node__Struct:

    def emit_declaration(self, m):
        name = m._shortname(self)
        with m.block("class %s(__.Struct):" % name):
            children = m.children[self.id]
            empty = True
            for child in children:
                if child.which() == schema.Node.__tag__.struct:
                    child.emit_declaration(m)
                    empty = False
            if empty:
                m.w("pass")

    def emit_definition(self, m):
        name = m._pyname(self)
        shortname = m._shortname(self)
        m.w("")
        m.w("@{name}.__extend__", name=name)
        with m.block("class {shortname}:", shortname=shortname):
            data_size = self.struct.dataWordCount
            ptrs_size = self.struct.pointerCount
            m.w("__data_size__ = %d" % data_size)
            m.w("__ptrs_size__ = %d" % ptrs_size)
            for child in m.children[self.id]:
                which = child.which()
                if which == schema.Node.__tag__.const:
                    m.visit_const(child)
                elif which == schema.Node.__tag__.struct:
                    child.emit_definition(m)
                else:
                    assert False
            if self.struct.discriminantCount:
                self._emit_tag(m)
            if self.struct.fields is not None:
                for field in self.struct.fields:
                    field.emit(m, self)
                self._emit_ctors(m)

    def _emit_tag(self, m):
        # union tags are 16 bits, so *2
        tag_offset = self.struct.discriminantOffset * 2
        enum_items = [None] * self.struct.discriminantCount
        for field in self.struct.fields:
            i = field.discriminantValue
            if i != schema.Field.noDiscriminant:
                enum_items[i] = m._field_name(field)
        enum_name = '%s.__tag__' % m._shortname(self)
        m.w("__tag_offset__ = %s" % tag_offset)
        m.declare_enum('__tag__', enum_name, enum_items)

    def _emit_ctors(self, m):
        if self.struct.discriminantCount:
            self._emit_ctors_union(m)
        else:
            self._emit_ctor_nounion(m)

    def _emit_ctor_nounion(self, m):
        data_size = self.struct.dataWordCount
        ptrs_size = self.struct.pointerCount
        ctor = Structor(m, '__new', data_size, ptrs_size, self.struct.fields)
        ctor.declare(m.code)
        #
        with m.code.def_('__init__', ['self'] + ctor.argnames):
            call = m.code.call('self.__new', ctor.argnames)
            m.w('buf = {call}', call=call)
            m.w('self._init(buf, 0, None)')

    def _emit_ctors_union(self, m):
        # suppose we have a tag whose members are 'circle' and 'square': we
        # create three ctors:
        #
        #     def __init__(self, x, y, square=undefined, circle=undefined):  ...
        #
        #     @classmethod
        #     def new_square(cls, x, y): ...
        #
        #     @classmethod
        #     def new_circle(cls, x, y): ...
        #
        # when calling __init__, one and only one of square and circle must be given. 
        #
        data_size = self.struct.dataWordCount
        ptrs_size = self.struct.pointerCount
        tag_offset = self.struct.discriminantOffset * 2
        #
        std_fields = [] # non-union fields
        tag_fields = [] # union fields
        for f in self.struct.fields:
            if f.discriminantValue == schema.Field.noDiscriminant:
                std_fields.append(f)
            else:
                tag_fields.append(f)
        #
        # now, we create a separate ctor for each tag value
        for tag_field in tag_fields:
            fields = [tag_field] + std_fields
            tag_name  = m._field_name(tag_field)
            ctor_name = '__new_' + tag_name
            ctor = Structor(m, ctor_name, data_size, ptrs_size, fields,
                            tag_offset, tag_field.discriminantValue)
            ctor.declare(m.code)
            #
            m.w('@classmethod')
            with m.code.def_('new_' + tag_name, ['cls'] + ctor.argnames):
                call = m.code.call('cls.' + ctor_name, ctor.argnames)
                m.w('buf = {call}', call=call)
                m.w('return cls.from_buffer(buf, 0, None)')
        #
        # finally, create the __init__
        # def __init__(cls, x, y, square=undefined, circle=undefined):
        #     if square is not undefined:
        #         self._assert_undefined(circle, 'circle', 'square')
        #         buf = cls.__new_squadre(x=x, y=y)
        #         self._init(buf, 0, None)
        #         return
        #     if circle is not undefined:
        #         self._assert_undefined(square, 'square', 'circle')
        #         buf = cls.__new_circle(x=x, y=y)
        #         self._init(buf, 0, None)
        #         return
        #     raise TypeError("one of the following args is required: square, circle")
        args = [m._field_name(f) for f in std_fields]
        for f in tag_fields:
            args.append('%s=__.undefined' % m._field_name(f))
        with m.block('def __init__(self, {arglist}):', arglist=m.code.args(args)):
            for tag_field in tag_fields:
                tag_field_name = m._field_name(tag_field)
                with m.block('if {name} is not __.undefined:', name=tag_field_name):
                    # emit the series of _assert_undefined, for each other tag field
                    for other_tag_field in tag_fields:
                        if other_tag_field is tag_field:
                            continue
                        m.w('self._assert_undefined({fname}, "{fname}", "{myname}")',
                            fname=m._field_name(other_tag_field),
                            myname=tag_field_name)
                    #
                    # return cls.new_square(x=x, y=y)
                    args = [m._field_name(f) for f in std_fields]
                    args.append(m._field_name(tag_field))
                    args = ['%s=%s' % (arg, arg) for arg in args]
                    m.w('buf = self.__new_{ctor}({args})',
                        ctor=tag_field_name, args=m.code.args(args))
                    m.w('self._init(buf, 0, None)')
                    m.w('return')
            #
            tags = [m._field_name(f) for f in tag_fields]
            tags = ', '.join(tags)
            m.w('raise TypeError("one of the following args is required: {tags}")',
                tags=tags)
