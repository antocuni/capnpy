import six
from capnpy.schema import CodeGeneratorRequest
from capnpy.compiler.module import ModuleGenerator

# main API entry point for end users
def get_reflection_data(module):
    try:
        return module._reflection_data
    except AttributeError:
        raise ValueError("%s does not seem to be a capnpy-generated module" %
                         module)


class ReflectionData(object):

    # subclasses are supposed to fill these fields accordingly
    request_data = None
    convert_case = False
    pyx = False

    # ModuleGenerator, initialized lazily
    _m = None
    @property
    def m(self):
        if self._m is not None:
            return self._m
        #
        request = CodeGeneratorRequest.loads(self.request_data)
        self._m = ModuleGenerator(request, convert_case=self.convert_case,
                                  version_check=True,
                                  pyx=self.pyx, standalone=True)
        return self._m

    def get_node(self, obj=None):
        """
        Get the schema.Node corresponding to obj. Obj can be either:

            - an integer representing the node ID

            - a capnpy-generated object which has a __capnpy_id__ attribute,
              such as modules, types or annotations
        """
        if isinstance(obj, six.integer_types):
            id = obj
        else:
            id = obj.__capnpy_id__
        return self.m.allnodes[id]

    def has_annotation(self, entity, anncls):
        if hasattr(entity, '__capnpy_id__'):
            entity = self.get_node(entity)
        return self.m.has_annotation(entity, anncls)
