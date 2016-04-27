import py
import keyword
from collections import defaultdict
from pypytools.codegen import Code
from capnpy.convert_case import from_camel_case

# the following imports have side-effects, and augment the schema.* classes
# with emit() methods
import capnpy.compiler.request
import capnpy.compiler.node
import capnpy.compiler.struct_
import capnpy.compiler.field
import capnpy.compiler.misc

class ModuleGenerator(object):

    def __init__(self, request, convert_case, pyx, standalone):
        self.code = Code(pyx=pyx)
        self.request = request
        self.convert_case = convert_case
        self.pyx = pyx
        self.standalone = standalone
        self.allnodes = {} # id -> node
        self.children = defaultdict(list) # nodeId -> nested nodes
        self.importnames = {} # filename -> import name
        self.extra_annotations = defaultdict(list) # obj -> [ann]

    def register_extra_annotation(self, obj, ann):
        self.extra_annotations[obj].append(ann)

    def has_annotation(self, obj, anncls):
        annotations = self.extra_annotations.get(obj, [])
        if obj.annotations is not None:
            annotations += obj.annotations
        for ann in annotations:
            if ann.id == anncls.__id__:
                return ann
        return None

    def w(self, *args, **kwargs):
        self.code.w(*args, **kwargs)

    def block(self, *args, **kwargs):
        return self.code.block(*args, **kwargs)

    def register_import(self, fname):
        name = py.path.local(fname).purebasename
        name = name.replace('+', 'PLUS')
        name = '_%s_capnp' % name
        if name in self.importnames.values():
            # avoid name clashes
            name = '%s_%s' % (name, len(self.filenames))
        self.importnames[fname] = name
        return name

    def generate(self):
        self.request.emit(self)
        return self.code.build()

    def _dump_node(self, node):
        def visit(node, deep=0):
            print '%s%s: %s' % (' ' * deep, node.which(), node.displayName)
            for child in self.children[node.id]:
                visit(child, deep+2)
        visit(node)

    def _convert_name(self, name):
        if self.convert_case:
            return from_camel_case(name)
        else:
            return name

    def _field_name(self, field):
        name = self._convert_name(field.name)
        name = self._mangle_name(name)
        return name

    def _mangle_name(self, name):
        if name in keyword.kwlist:
            return name + '_'
        return name

    def declare_enum(self, var_name, enum_name, items):
        # this method cannot go on Node__Enum because it's also called by
        # Node__Struct (for __tag__)
        items = map(repr, items)
        decl = "%s = _enum(%r, [%s])" % (var_name, enum_name, ', '.join(items))
        self.w(decl)

    def def_property(self, ns, name, src):
        if self.pyx:
            with ns.block('property {name}:', name=name):
                with ns.block('def __get__(self):'):
                    ns.ww(src)
        else:
            ns.w('@property')
            with ns.block('def {name}(self):', name=name):
                ns.ww(src)
        ns.w()

    def robust_arglist(self, argnames):
        # in pyx mode, we cannot use e.g. 'void' as argname: we need to use
        # 'object void', else cython complains.
        if self.pyx:
            def addtype(name):
                if name.startswith('*'):
                    return name
                return 'object %s' % name
            argnames = [addtype(name) for name in argnames]
        return argnames
