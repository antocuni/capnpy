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


class Node(AbstractNode):

    def __init__(self, m, f, prefix):
        self.f = f
        self.varname = m._field_name(f)
        if prefix:
            self.varname = '%s_%s' % (prefix, self.varname)
        self.children = []
        if f.is_group():
            group = m.allnodes[f.group.typeId]
            for fchild in group.struct.fields:
                child = Node(m, fchild, prefix=self.varname)
                self.children.append(child)

    def __repr__(self):
        return '<Node %s: %s>' % (self.varname, self.f.which())
