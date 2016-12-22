from capnpy import annotate
from capnpy import schema
from capnpy.type import Types
from capnpy.compiler.structor import Structor
from capnpy.compiler.fieldtree import FieldTree

try:
    from capnpy import _hash
except ImportError:
    _hash = None # this is needed only in PYX mode

@schema.Node__Struct.__extend__
class Node__Struct:

    def emit_declaration(self, m):
        children = m.children[self.id]
        for child in children:
            child.emit_declaration(m)
        #
        # find and register all groups having a $key annotation. We need to do
        # it here because we need this info when we emit the definition for
        # the group class
        for field in self.struct.fields or []:
            ann = m.has_annotation(field, annotate.key)
            if ann:
                assert field.is_group()
                groupnode = m.allnodes[field.group.typeId]
                m.register_extra_annotation(groupnode, ann)
        #
        ns = m.code.new_scope()
        ns.name = self.compile_name(m)
        ns.dotname = self.runtime_name(m)
        if m.pyx:
            ns.w("cdef class {name}(_Struct)")
        else:
            ns.w("class {name}(_Struct): pass")
            ns.w("{name}.__name__ = '{dotname}'")
        ns.w()

    def emit_definition(self, m):
        for child in m.children[self.id]:
            child.emit_definition(m)
        #
        ns = m.code.new_scope()
        ns.name = self.compile_name(m)
        ns.dotname = self.runtime_name(m)
        ns.data_size = self.struct.dataWordCount
        ns.ptrs_size = self.struct.pointerCount
        #
        if not m.pyx:
            # use the @extend decorator only in Pure Python mode: in pyx mode
            # it is (1) not allowed and (2) useless anyway, because we have
            # forward-declared the class, not defined it
            ns.w("@{name}.__extend__")
        #
        with ns.block("{cdef class} {name}(_Struct):"):
            ns.ww("""
                __static_data_size__ = {data_size}
                __static_ptrs_size__ = {ptrs_size}

            """)
            for child in m.children[self.id]:
                child.emit_reference_as_child(m)
            m.w()
            if self.struct.discriminantCount:
                self._emit_union_tag(m)
            if self.struct.fields is not None:
                for field in self.struct.fields:
                    field.emit(m, self)
                self._emit_ctors(m)
            self._emit_repr(m)
            self._emit_key_maybe(m)
        ns.w()
        ns.w()

    def emit_reference_as_child(self, m):
        if self.is_nested(m) and not self.struct.isGroup:
            m.w('{shortname} = {name}', shortname=self.shortname(m),
                name=self.compile_name(m))

    def emit_delete_nested_from_globals(self, m):
        if self.is_nested(m) and not self.struct.isGroup:
            m.w("del globals()['{name}']", name=self.compile_name(m))
        for child in m.children[self.id]:
            child.emit_delete_nested_from_globals(m)

    def _emit_union_tag(self, m):
        # union tags are 16 bits, so *2
        ns = m.code.new_scope()
        ns.tag_offset = self.struct.discriminantOffset * 2
        enum_items = [None] * self.struct.discriminantCount
        for field in self.struct.fields:
            if field.is_part_of_union():
                enum_items[field.discriminantValue] = m._field_name(field)
        enum_name = '%s.__tag__' % self.shortname(m)
        ns.w("__tag_offset__ = {tag_offset}")
        m.declare_enum('__tag__', enum_name, enum_items)
        ns.w()
        if m.pyx:
            # generate a specialized version of __which__, which does not need to
            # do a lookup for __tag_offset__. Not needed on PyPy because the
            # default __which__() implemented in struct_.py is already fast
            ns.ww("""
                cpdef long __which__(self) except -1:
                    return self._read_data_int16({tag_offset})
            """)
            ns.w()
        #
        for i, item in enumerate(enum_items):
            ns.item = item
            ns.i = i
            ns.ww("""
                def is_{item}(self):
                    return self._read_data_int16({tag_offset}) == {i}
            """)
        ns.w()

    def _emit_ctors(self, m):
        if self.struct.isGroup:
            return
        ns = m.code.new_scope()
        ns.data_size = self.struct.dataWordCount
        ns.ptrs_size = self.struct.pointerCount
        named_union = self.struct.get_unique_named_union(m)
        self._emit_init(m, ns)
        self._emit_ctors_union(m, ns)

    def _emit_init(self, m, ns):
        tag_offset = None
        if self.struct.is_union():
            tag_offset = self.struct.discriminantOffset * 2
        ctor = Structor(m, ns.data_size, ns.ptrs_size, self.struct.fields,
                        tag_offset=tag_offset)
        ctor.emit(m.code)
        ns.w()
        with ns.def_('__init__', ['self'] + ctor.params):
            call = m.code.call('self.__new', ctor.argnames)
            ns.w('_buf = {call}', call=call)
            ns.w('_Struct.__init__(self, _buf, 0, {data_size}, {ptrs_size})')
        ns.w()

    def _emit_ctors_union(self, m, ns):
        for f in self.struct.fields:
            if f.is_part_of_union():
                tag_field = f
                fields = [f for f in self.struct.fields
                          if not f.is_part_of_union() or f == tag_field]
                self._emit_one_ctor_union(m, ns, fields, tag_field)

    def _emit_one_ctor_union(self, m, ns, fields, tag_field):
        ## def new_foo(cls, x=0, y=0):
        ##     buf = self.__new(x=x, y=y, foo=None)
        ##     return cls.from_buffer(buf, 0, ..., ...)
        tag_name = m._field_name(tag_field)
        name = 'new_' + tag_name
        fieldtree = FieldTree(m, fields)
        argnames, params = fieldtree.get_args_and_params()
        argnames = [(arg, arg) for arg in argnames]
        if tag_field.is_void():
            # in case of a void tag field, we need to explicitly pass it
            # to the __init__, because it's not in argnames
            argnames.append((tag_name, 'None'))
        #
        ns.w('@classmethod')
        with ns.def_(name, ['cls'] + params):
            call = m.code.call('cls.__new', argnames)
            ns.w('buf = {call}', call=call)
            ns.w('return cls.from_buffer(buf, 0, {data_size}, {ptrs_size})')
        ns.w()

    def _emit_repr(self, m):
        # def shortrepr(self):
        #     parts = []
        #     parts.append("x = %s" % self.x)
        #     parts.append("x = %s" % self.y)
        #     return "(%s)" % ", ".join(parts)
        #
        with m.block('{cpdef} shortrepr(self):') as ns:
            fields = self.struct.fields or []
            ns.w('parts = []')
            for f in fields:
                ns.fname = m._field_name(f)
                ns.fieldrepr = self._shortrepr_for_field(ns, f)
                ns.append = ns.format('parts.append("{fname} = %s" % {fieldrepr})')
                ns.is_default_field = bool(f.discriminantValue == 0)
                #
                if f.is_part_of_union() and f.is_pointer():
                    # normally, null fields are never shown. However, in case
                    # of unions, the currently-tagged field is always shown
                    # (and if it's null we simply show its default value).
                    # HOWEVER, if the tagged field is the default one AND if
                    # it's null, we don't show anything; see
                    # test_union_set_but_null_pointer for examples.
                    ns.ww("""
                    if self.is_{fname}() and (self.has_{fname}() or
                                              not {is_default_field}):
                        {append}
                    """)
                elif f.is_part_of_union():
                    ns.w("if self.is_{fname}(): {append}")
                elif f.is_pointer():
                    ns.w("if self.has_{fname}(): {append}")
                else:
                    ns.w("{append}")
            ns.w('return "(%s)" % ", ".join(parts)')

    def _shortrepr_for_field(self, ns, f):
        if f.is_float32():
            return ns.format('_float32_repr(self.{fname})')
        elif f.is_float64():
            return ns.format('_float64_repr(self.{fname})')
        if f.is_primitive() or f.is_enum():
            return ns.format('self.{fname}')
        elif f.is_bool():
            return ns.format('str(self.{fname}).lower()')
        elif f.is_void():
            return '"void"'
        elif f.is_text() or f.is_data():
            return ns.format('_text_repr(self.get_{fname}())')
        elif f.is_struct() or f.is_list():
            return ns.format('self.get_{fname}().shortrepr()')
        elif f.is_group():
            return ns.format('self.{fname}.shortrepr()')
        else:
            return '"???"'

    def _emit_key_maybe(self, m):
        ann = m.has_annotation(self, annotate.key)
        if ann is None:
            return
        assert ann.annotation.value.is_text()
        allfields = [f.name for f in self.struct.fields]
        # we expect keyfields to be something like "x, y, z" or "*"
        txt = ann.annotation.value.text.strip()
        if txt == '*':
            fieldnames = allfields
        else:
            fieldnames = map(str.strip, txt.split(','))
        #
        # sanity check
        for f in fieldnames:
            if f not in allfields:
                raise ValueError("Error in $Py.key: the field '%s' does not exist" % f)
        #
        ns = m.code.new_scope()
        ns.key = ', '.join(['self.%s' % m._convert_name(f) for f in fieldnames])
        ns.w()
        ns.ww("""
            def _key(self):
                return ({key},)
        """) # the trailing comma is to ensure a tuple even if there is a single field
        #
        if m.pyx:
            self._emit_fash_hash(m, fieldnames)

    def _emit_fash_hash(self, m, fieldnames):
        # emit a specialized, fast __hash__.
        fields = dict([(f.name, f) for f in self.struct.fields])
        m.w()
        with m.code.block('def __hash__(self):') as ns:
            ns.n = len(fieldnames)
            ns.w('cdef long h[{n}]')
            # compute the hash of each field
            for ns.i, fname in enumerate(fieldnames):
                f = fields[fname]
                ns.fname = m._convert_name(fname)
                if f.is_text():
                    ns.offset = f.slot.offset * f.slot.get_size()
                    ns.w('h[{i}] = self._hash_str_text({offset})')
                else:
                    ns.hash = self._fasthash_for_field(f)
                    ns.w('h[{i}] = {hash}(self.{fname})')
            #
            # compute the hash of the whole tuple
            ns.w('return _hash.tuplehash(h, {n})')
        #
        # XXX this is a hack/workaround for what it looks like a Cython bug:
        # apparently, we need to redefine __richcmp__ together with __hash__,
        # else the base one is not going to be called.  Moreover, for no good
        # reason "self" is typed as PyObject* instead of being given the
        # precise type, so we cast to Struct_ to force early binding
        ns.w()
        ns.ww("""
            def __richcmp__(self, other, op):
                return (<_Struct>self)._richcmp(other, op)
        """)

    def _fasthash_for_field(self, f):
        if not f.is_slot():
            return 'hash'
        t = f.slot.type
        w = t.which()
        if schema.Type.__tag__.int8 <= w <= schema.Type.__tag__.uint32:
            # this can be assimilated to a Python <int>
            return '_hash.inthash'
        elif t.is_uint64():
            # this can be assimilated to a Python <long>
            return '_hash.longhash'
        else:
            # no fast hash, use the "slow" one
            return 'hash'

