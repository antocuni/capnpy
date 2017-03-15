from capnpy.schema import Node, Node__Enum, Node__Const, Node__Annotation

# The implementation of each node is divided in three parts:
#     1. forward declaration
#     2. definition
#     3. reference as child
#
# They are slightly different in pyx or python mode. It is probably easier to
# explain by giving an example in each mode.
#
# PYTHON MODE
#
#     class Outer__Nested: pass  # forward declaration
#     class Outer: pass          # forward declaration
#
#     # definition of Outer__Nested
#     @Outer__Nested.__extend__
#     class Outer__Nested:
#         ...
#
#     # definition of Outer
#     @Outer.__extend__
#     class Outer:
#         ...
#         Nested = Outer__Nested # reference as child
#
# PYX MODE
#
#     cdef class Outer__Nested  # forward declaration
#     cdef class Outer          # forward declaration
#
#     # definition of Outer__Nested
#     cdef class Outer__Nested:
#         ...
#
#     # definition of Outer
#     cdef class Outer:
#         ...
#         Nested = Outer__Nested # reference as child


@Node.__extend__
class Node:

    def get_parent(self, m):
        if self.scopeId == 0:
            return None
        return m.allnodes[self.scopeId]

    def is_nested(self, m):
        parent = self.get_parent(m)
        return parent.scopeId != 0

    def is_imported(self, m):
        node = self
        while node is not None:
            if node.is_file() and node != m.current_scope:
                return True
            node = node.get_parent(m)
        return False

    def shortname(self, m):
        name = self.displayName[self.displayNamePrefixLength:]
        if self.is_file():
            filename = self.displayName
            return m.importnames[filename]
        return name

    def _fullname(self, m, sep):
        parent = self.get_parent(m)
        if parent is None or parent == m.current_scope:
            return self.shortname(m)
        return '%s%s%s' % (parent._fullname(m, sep), sep, self.shortname(m))

    def compile_name(self, m):
        if self.is_imported(m):
            return self.runtime_name(m)
        return self._fullname(m, '_')

    def runtime_name(self, m):
        return self._fullname(m, '.')

    def emit_declaration(self, m):
        assert False, 'Unkown node type: %s' % self.which()

    def emit_definition(self, m):
        pass # do nothing by default

    def emit_reference_as_child(self, m):
        pass # do nothing by default


@Node__Annotation.__extend__
class Node__Annotation:

    def emit_declaration(self, m):
        ns = m.code.new_scope()
        ns.name = self.shortname(m)
        ns.id = self.id
        ns.targets_file = self.annotation.targetsFile
        ns.targets_const = self.annotation.targetsConst
        ns.targets_enum = self.annotation.targetsEnum
        ns.targets_enumerant = self.annotation.targetsEnumerant
        ns.targets_struct = self.annotation.targetsStruct
        ns.targets_field = self.annotation.targetsField
        ns.targets_union = self.annotation.targetsUnion
        ns.targets_group = self.annotation.targetsGroup
        ns.targets_interface = self.annotation.targetsInterface
        ns.targets_method = self.annotation.targetsMethod
        ns.targets_param = self.annotation.targetsParam
        ns.targets_annotation = self.annotation.targetsAnnotation
        ns.ww("""
            class {name}(object):
                __id__ = {id}
                targets_file = {targets_file}
                targets_const = {targets_const}
                targets_enum = {targets_enum}
                targets_enumerant = {targets_enumerant}
                targets_struct = {targets_struct}
                targets_field = {targets_field}
                targets_union = {targets_union}
                targets_group = {targets_group}
                targets_interface = {targets_interface}
                targets_method = {targets_method}
                targets_param = {targets_param}
                targets_annotation = {targets_annotation}
        """)

@Node__Enum.__extend__
class Node__Enum:

    def emit_declaration(self, m):
        name =  self.compile_name(m)
        items = [m._field_name(item) for item in self.enum.enumerants]
        m.declare_enum(name, self.shortname(m), items)
        m.w('_{name}_list_item_type = _EnumItemType({name})', name=name)
        m.w()

    def emit_reference_as_child(self, m):
        if self.is_nested(m):
            m.w("{shortname} = {name}", shortname=self.shortname(m),
                name=self.compile_name(m))

@Node__Const.__extend__
class Node__Const:

    def emit_declaration(self, m):
        pass

    def emit_reference_as_child(self, m):
        # XXX: this works only for numerical consts so far
        name = self.shortname(m)
        val = self.const.value.as_pyobj()
        m.w("%s = %s" % (name, val))
