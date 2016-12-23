from collections import namedtuple

Union = namedtuple('Union', ['varname', 'offset'])

class AbstractNode(object):

    parent = None
    union = None
    children = ()

    def pprint(self, level=0):
        indent = (level*4) * ' '
        print '%s%s' % (indent, self)
        for child in self.children:
            child.pprint(level+1)

    def allnodes(self):
        """
        Iterates over all nodes of the tree, in pre-order.
        """
        for child in self.children:
            yield child
            for node in child.allnodes():
                yield node

    def _add_children(self, m, fields, prefix, field_force_default):
        for f in fields:
            # union fields are always included, even if they are void
            if f.is_void() and not f.is_part_of_union():
                continue
            node = Node(m, f, prefix, field_force_default)
            node.parent = self
            self.children.append(node)


class FieldTree(AbstractNode):
    """
    Tree of fields of a struct.

    Each node can be a group or a slot; all leaves are slots.
    """

    def __init__(self, m, struct_or_fields, field_force_default=None):
        if isinstance(struct_or_fields, list):
            self.struct = None
            fields = struct_or_fields
        else:
            self.struct = struct_or_fields
            fields = self.struct.fields
        #
        if self.struct and self.struct.is_union():
            self.union = Union('anonymous', self.struct.discriminantOffset*2)
        #
        self.children = []
        prefix = None
        self._add_children(m, fields, prefix, field_force_default)

    def __repr__(self):
        return '<FieldTree>'

    def all_unions(self):
        if self.union:
            yield self.union
        for node in self.allnodes():
            if node.union:
                yield node.union

    def get_args_and_params(self):
        """
        Return argnames and params, to be used to emit ctors and other functions.

          - argnames are the plain variable names

          - params are tuples (varname, default), where default is a *string*
            which when eval()ued computes the default value of the parameter

        Note that the arguments taken by the ctor corresponds to the varname
        of the *first* level of the tree
        """
        argnames = []
        params = []
        for node in self.children:
            argnames.append(node.varname)
            params.append((node.varname, node.default))
        return argnames, params


class Node(AbstractNode):

    def __init__(self, m, f, prefix, field_force_default):
        self.f = f
        self.force_default = (field_force_default and f == field_force_default)
        self.varname = m._field_name(f)
        if prefix:
            self.varname = '%s_%s' % (prefix, self.varname)
        self._init_children(m, field_force_default)
        self._init_default(m)

    def _init_children(self, m, field_force_default):
        self.children = []
        if self.f.is_group():
            group = m.allnodes[self.f.group.typeId]
            self._add_children(m, group.struct.fields, prefix=self.varname,
                               field_force_default=field_force_default)
            if group.struct.is_union():
                self.union = Union(self.varname, group.struct.discriminantOffset*2)

    def _init_default(self, m):
        # self.default is a *string* containing a Python repr of the default
        # value
        if self.f.is_part_of_union() and not self.force_default:
            self.default = '_undefined'
        elif self.f.is_slot():
            default_val = self.f.slot.defaultValue.as_pyobj()
            self.default = str(default_val)
        else:
            assert self.f.is_group()
            items = [child.default for child in self.children]
            self.default = '(%s,)' % ', '.join(items)

    def __repr__(self):
        return '<Node %s: %s>' % (self.varname, self.f.which())
