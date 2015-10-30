from capnpy import schema
from capnpy.util import extend

@extend(schema.Node)
class Node:

    def emit_declaration(self, m):
        if self.which() == schema.Node.__tag__.annotation:
            # annotations are simply ignored for now
            pass
        else:
            assert False, 'Unkown node type: %s' % which

    def emit_definition(self, m):
        pass # do nothing by default


@extend(schema.Node__Enum)
class Node__Enum:

    def emit_declaration(self, m):
        m.visit_enum(self)
