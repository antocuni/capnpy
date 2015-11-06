from capnpy.schema import Node, Node__Enum, Node__Const

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

    def shortname(self):
        name = self.displayName[self.displayNamePrefixLength:]
        if self.is_file():
            # XXX fix this mess
            import py
            fname = self.displayName
            return '_%s_capnp' % py.path.local(fname).purebasename
        elif self.is_struct() and self.struct.isGroup:
            return '_group_%s' % name
        return name

    def _fullname(self, m, sep):
        parent = self.get_parent(m)
        if parent is None or parent == m.current_scope:
            return self.shortname()
        return '%s%s%s' % (parent._fullname(m, sep), sep, self.shortname())

    def compile_name(self, m):
        if self.is_imported(m):
            return self.runtime_name(m)
        return self._fullname(m, '_')

    def runtime_name(self, m):
        return self._fullname(m, '.')

    def emit_declaration(self, m):
        if self.is_annotation():
            # annotations are simply ignored for now
            pass
        else:
            assert False, 'Unkown node type: %s' % self.which()

    def emit_definition(self, m):
        pass # do nothing by default

    def emit_reference_as_child(self, m):
        pass # do nothing by default

    def emit_delete_nested_from_globals(self, m):
        pass

@Node__Enum.__extend__
class Node__Enum:

    def emit_declaration(self, m):
        name = self.shortname()
        items = [m._field_name(item) for item in self.enum.enumerants]
        m.declare_enum(name, name, items)



@Node__Const.__extend__
class Node__Const:

    def emit_declaration(self, m):
        pass

    def emit_reference_as_child(self, m):
        # XXX: this works only for numerical consts so far
        name = self.shortname()
        val = self.const.value.as_pyobj()
        m.w("%s = %s" % (name, val))
