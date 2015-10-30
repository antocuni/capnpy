from capnpy import schema
from capnpy.util import extend

@extend(schema.CodeGeneratorRequest)
class CodeGeneratorRequest:

    def emit(self, m):
        for node in self.nodes:
            m.allnodes[node.id] = node
            # roots have scopeId == 0, so children[0] will contain them
            m.children[node.scopeId].append(node)
        #
        for f in self.requestedFiles:
            m.visit_file(f)

