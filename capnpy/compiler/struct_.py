from capnpy import schema
from capnpy.util import extend


@extend(schema.Node__Struct)
class Node__Struct:

    def emit_declaration(self, m):
        name = m._shortname(self)
        with m.block("class %s(__.Struct):" % name):
            for child in m.children[self.id]:
                if child.which() == schema.Node.__tag__.struct:
                    child.emit_declaration(m)
            m.w("pass")

    def emit_definition(self, m):
        m.visit_struct(self)

