from capnpy import schema

@schema.Node__Enum.__extend__
class Node__Enum:

    def compute_options(self, m, parent_opt):
        # compute the options for the children nodes
        super(schema.Node__Enum, self).compute_options(m, parent_opt)
        # and also for the fields
        opt = m.options(self)
        for e in self.get_enum_enumerants():
            e.compute_options(m, opt)

    def emit_declaration(self, m):
        name =  self.compile_name(m)
        items = [m.py_field_name(item) for item in self.get_enum_enumerants()]
        m.declare_enum(name, self.shortname(m), self.id, items)
        m.w('_{name}_list_item_type = _EnumItemType({name})', name=name)
        m.w()

    def emit_reference_as_child(self, m):
        if self.is_nested(m):
            m.w("{shortname} = {name}", shortname=self.shortname(m),
                name=self.compile_name(m))


@schema.Enumerant.__extend__
class Enumerant:

    def compute_options(self, m, parent_opt):
        m.compute_options_generic(self, parent_opt)
