class AbstractNode(object):

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

    def allslots(self):
        """
        Iterates over all leaves of the tree.
        """
        for node in self.allnodes():
            if node.f.is_slot():
                yield node


class FieldTree(AbstractNode):
    """
    Tree of fields of a struct.

    Each node can be a group or a slot; all leaves are slots.
    """

    def __init__(self, m, fields):
        self.children = []
        for f in fields:
            node = Node(m, f, prefix=None)
            self.children.append(node)

    def __repr__(self):
        return '<FieldTree>'

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

    def __init__(self, m, f, prefix):
        self.f = f
        self.varname = m._field_name(f)
        if prefix:
            self.varname = '%s_%s' % (prefix, self.varname)
        self._init_children(m)
        # self.default is a *string* containing a Python repr of the default
        # value
        self._init_default(m)

    def _init_children(self, m):
        self.children = []
        if self.f.is_group():
            group = m.allnodes[self.f.group.typeId]
            for fchild in group.struct.fields:
                child = Node(m, fchild, prefix=self.varname)
                self.children.append(child)

    def _init_default(self, m):
        if self.f.is_slot():
            default_val = self.f.slot.defaultValue.as_pyobj()
            self.default = str(default_val)
        else:
            assert self.f.is_group()
            items = [child.default for child in self.children]
            self.default = '(%s,)' % ', '.join(items)

    def __repr__(self):
        return '<Node %s: %s>' % (self.varname, self.f.which())
