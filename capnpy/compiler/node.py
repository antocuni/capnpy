from capnpy.schema import Node, Node__Enum, Node__Const

@Node.__extend__
class Node:

    def emit_declaration(self, m):
        if self.which() == Node.__tag__.annotation:
            # annotations are simply ignored for now
            pass
        else:
            assert False, 'Unkown node type: %s' % self.which()

    def emit_definition(self, m):
        pass # do nothing by default


@Node__Enum.__extend__
class Node__Enum:

    def emit_declaration(self, m):
        name = m._shortname(self)
        items = [m._field_name(item) for item in self.enum.enumerants]
        m.declare_enum(name, name, items)



@Node__Const.__extend__
class Node__Const:

    def emit_declaration(self, m):
        pass

    def emit_definition(self, m):
        # XXX: this works only for numerical consts so far
        name = m._shortname(self)
        val = self.const.value.as_pyobj()
        m.w("%s = %s" % (name, val))
