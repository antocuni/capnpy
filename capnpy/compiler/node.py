from capnpy import schema

@schema.Node.__extend__
class Node:

    def emit_declaration(self, m):
        if self.which() == schema.Node.__tag__.annotation:
            # annotations are simply ignored for now
            pass
        else:
            assert False, 'Unkown node type: %s' % self.which()

    def emit_definition(self, m):
        pass # do nothing by default


@schema.Node__Enum.__extend__
class Node__Enum:

    def emit_declaration(self, m):
        name = m._shortname(self)
        items = [m._field_name(item) for item in self.enum.enumerants]
        m.declare_enum(name, name, items)



@schema.Node__Const.__extend__
class Node__Const:

    def emit_definition(self, m):
        # XXX: this works only for numerical consts so far
        name = m._shortname(self)
        val = m._get_value(self.const.value)
        m.w("%s = %s" % (name, val))
