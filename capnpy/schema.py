# THIS FILE HAS BEEN GENERATED AUTOMATICALLY BY capnpy
# do not edit by hand
# generated on 2016-01-20 16:17
# input files: 
#   - capnpy/schema.capnp

from capnpy.struct_ import Struct as _Struct
from capnpy.struct_ import undefined as _undefined
from capnpy.enum import enum as _enum
from capnpy.blob import Types as _Types
from capnpy.builder import StructBuilder as _StructBuilder
from capnpy.list import PrimitiveList as _PrimitiveList
from capnpy.list import StructList as _StructList
from capnpy.list import StringList as _StringList
#_cPLUSPLUS_capnp = __compiler.load_schema("/capnp/c++.capnp")

#### FORWARD DECLARATIONS ####

class CodeGeneratorRequest_RequestedFile_Import(_Struct): pass
CodeGeneratorRequest_RequestedFile_Import.__name__ = 'CodeGeneratorRequest.RequestedFile.Import'

class CodeGeneratorRequest_RequestedFile(_Struct): pass
CodeGeneratorRequest_RequestedFile.__name__ = 'CodeGeneratorRequest.RequestedFile'

class CodeGeneratorRequest(_Struct): pass
CodeGeneratorRequest.__name__ = 'CodeGeneratorRequest'

class Method(_Struct): pass
Method.__name__ = 'Method'

class Enumerant(_Struct): pass
Enumerant.__name__ = 'Enumerant'

ElementSize = _enum('ElementSize', ('empty', 'bit', 'byte', 'twoBytes', 'fourBytes', 'eightBytes', 'pointer', 'inlineComposite'))

class Type_anyPointer_parameter(_Struct): pass
Type_anyPointer_parameter.__name__ = 'Type.anyPointer.parameter'

class Type_anyPointer_implicitMethodParameter(_Struct): pass
Type_anyPointer_implicitMethodParameter.__name__ = 'Type.anyPointer.implicitMethodParameter'

class Type_anyPointer(_Struct): pass
Type_anyPointer.__name__ = 'Type.anyPointer'

class Type_struct(_Struct): pass
Type_struct.__name__ = 'Type.struct'

class Type_enum(_Struct): pass
Type_enum.__name__ = 'Type.enum'

class Type_interface(_Struct): pass
Type_interface.__name__ = 'Type.interface'

class Type_list(_Struct): pass
Type_list.__name__ = 'Type.list'

class Type(_Struct): pass
Type.__name__ = 'Type'

class Field_group(_Struct): pass
Field_group.__name__ = 'Field.group'

class Field_ordinal(_Struct): pass
Field_ordinal.__name__ = 'Field.ordinal'

class Field_slot(_Struct): pass
Field_slot.__name__ = 'Field.slot'

class Field(_Struct): pass
Field.__name__ = 'Field'

class Superclass(_Struct): pass
Superclass.__name__ = 'Superclass'

class Value(_Struct): pass
Value.__name__ = 'Value'

class Brand_Binding(_Struct): pass
Brand_Binding.__name__ = 'Brand.Binding'

class Brand_Scope(_Struct): pass
Brand_Scope.__name__ = 'Brand.Scope'

class Brand(_Struct): pass
Brand.__name__ = 'Brand'

class Annotation(_Struct): pass
Annotation.__name__ = 'Annotation'

class Node_interface(_Struct): pass
Node_interface.__name__ = 'Node.interface'

class Node_const(_Struct): pass
Node_const.__name__ = 'Node.const'

class Node_struct(_Struct): pass
Node_struct.__name__ = 'Node.struct'

class Node_annotation(_Struct): pass
Node_annotation.__name__ = 'Node.annotation'

class Node_enum(_Struct): pass
Node_enum.__name__ = 'Node.enum'

class Node_NestedNode(_Struct): pass
Node_NestedNode.__name__ = 'Node.NestedNode'

class Node_Parameter(_Struct): pass
Node_Parameter.__name__ = 'Node.Parameter'

class Node(_Struct): pass
Node.__name__ = 'Node'


#### DEFINITIONS ####

@CodeGeneratorRequest_RequestedFile_Import.__extend__
class CodeGeneratorRequest_RequestedFile_Import(_Struct):
    __static_data_size__ = 1
    __static_ptrs_size__ = 1
    
    
    @property
    def id(self):
        # no union check
        value = self._read_data(0, ord('Q'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @property
    def name(self):
        # no union check
        return self._read_str_text(0)
    
    def has_name(self):
        offset, ptr = self._read_ptr(0)
        return ptr != 0
    
    @staticmethod
    def __new(id, name):
        builder = _StructBuilder('Qq')
        name = builder.alloc_string(8, name)
        buf = builder.build(id, name)
        return buf
    
    def __init__(self, id, name):
        buf = self.__new(id, name)
        _Struct.__init__(self, buf, 0, 1, 1)
    
    def shortrepr(self):
        parts = [
            "(",
            "id = ", str(self.id), ", ",
            "name = ", str(self.name), 
            ")"
            ]
        return "".join(parts)


@CodeGeneratorRequest_RequestedFile.__extend__
class CodeGeneratorRequest_RequestedFile(_Struct):
    __static_data_size__ = 1
    __static_ptrs_size__ = 2
    
    Import = CodeGeneratorRequest_RequestedFile_Import
    
    @property
    def id(self):
        # no union check
        value = self._read_data(0, ord('Q'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @property
    def filename(self):
        # no union check
        return self._read_str_text(0)
    
    def has_filename(self):
        offset, ptr = self._read_ptr(0)
        return ptr != 0
    
    @property
    def imports(self):
        # no union check
        return self._read_list(8, _StructList, CodeGeneratorRequest.RequestedFile.Import)
    
    def has_imports(self):
        offset, ptr = self._read_ptr(8)
        return ptr != 0
    
    @staticmethod
    def __new(id, filename, imports):
        builder = _StructBuilder('Qqq')
        filename = builder.alloc_string(8, filename)
        imports = builder.alloc_list(16, _StructList, CodeGeneratorRequest.RequestedFile.Import, imports)
        buf = builder.build(id, filename, imports)
        return buf
    
    def __init__(self, id, filename, imports):
        buf = self.__new(id, filename, imports)
        _Struct.__init__(self, buf, 0, 1, 2)
    
    def shortrepr(self):
        parts = [
            "(",
            "id = ", str(self.id), ", ",
            "filename = ", str(self.filename), ", ",
            "imports = ", str(self.imports), 
            ")"
            ]
        return "".join(parts)


@CodeGeneratorRequest.__extend__
class CodeGeneratorRequest(_Struct):
    __static_data_size__ = 0
    __static_ptrs_size__ = 2
    
    RequestedFile = CodeGeneratorRequest_RequestedFile
    
    @property
    def nodes(self):
        # no union check
        return self._read_list(0, _StructList, Node)
    
    def has_nodes(self):
        offset, ptr = self._read_ptr(0)
        return ptr != 0
    
    @property
    def requestedFiles(self):
        # no union check
        return self._read_list(8, _StructList, CodeGeneratorRequest.RequestedFile)
    
    def has_requestedFiles(self):
        offset, ptr = self._read_ptr(8)
        return ptr != 0
    
    @staticmethod
    def __new(nodes, requestedFiles):
        builder = _StructBuilder('qq')
        nodes = builder.alloc_list(0, _StructList, Node, nodes)
        requestedFiles = builder.alloc_list(8, _StructList, CodeGeneratorRequest.RequestedFile, requestedFiles)
        buf = builder.build(nodes, requestedFiles)
        return buf
    
    def __init__(self, nodes, requestedFiles):
        buf = self.__new(nodes, requestedFiles)
        _Struct.__init__(self, buf, 0, 0, 2)
    
    def shortrepr(self):
        parts = [
            "(",
            "nodes = ", str(self.nodes), ", ",
            "requestedFiles = ", str(self.requestedFiles), 
            ")"
            ]
        return "".join(parts)


@Method.__extend__
class Method(_Struct):
    __static_data_size__ = 3
    __static_ptrs_size__ = 5
    
    
    @property
    def name(self):
        # no union check
        return self._read_str_text(0)
    
    def has_name(self):
        offset, ptr = self._read_ptr(0)
        return ptr != 0
    
    @property
    def codeOrder(self):
        # no union check
        value = self._read_data(0, ord('H'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @property
    def paramStructType(self):
        # no union check
        value = self._read_data(8, ord('Q'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @property
    def resultStructType(self):
        # no union check
        value = self._read_data(16, ord('Q'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @property
    def annotations(self):
        # no union check
        return self._read_list(8, _StructList, Annotation)
    
    def has_annotations(self):
        offset, ptr = self._read_ptr(8)
        return ptr != 0
    
    @property
    def paramBrand(self):
        # no union check
        return self._read_struct(16, Brand)
    
    def has_paramBrand(self):
        offset, ptr = self._read_ptr(16)
        return ptr != 0
    
    @property
    def resultBrand(self):
        # no union check
        return self._read_struct(24, Brand)
    
    def has_resultBrand(self):
        offset, ptr = self._read_ptr(24)
        return ptr != 0
    
    @property
    def implicitParameters(self):
        # no union check
        return self._read_list(32, _StructList, Node.Parameter)
    
    def has_implicitParameters(self):
        offset, ptr = self._read_ptr(32)
        return ptr != 0
    
    @staticmethod
    def __new(name, codeOrder, paramStructType, resultStructType, annotations, paramBrand, resultBrand, implicitParameters):
        builder = _StructBuilder('HxxxxxxQQqqqqq')
        name = builder.alloc_string(24, name)
        annotations = builder.alloc_list(32, _StructList, Annotation, annotations)
        paramBrand = builder.alloc_struct(40, Brand, paramBrand)
        resultBrand = builder.alloc_struct(48, Brand, resultBrand)
        implicitParameters = builder.alloc_list(56, _StructList, Node.Parameter, implicitParameters)
        buf = builder.build(codeOrder, paramStructType, resultStructType, name, annotations, paramBrand, resultBrand, implicitParameters)
        return buf
    
    def __init__(self, name, codeOrder, paramStructType, resultStructType, annotations, paramBrand, resultBrand, implicitParameters):
        buf = self.__new(name, codeOrder, paramStructType, resultStructType, annotations, paramBrand, resultBrand, implicitParameters)
        _Struct.__init__(self, buf, 0, 3, 5)
    
    def shortrepr(self):
        parts = [
            "(",
            "name = ", str(self.name), ", ",
            "codeOrder = ", str(self.codeOrder), ", ",
            "paramStructType = ", str(self.paramStructType), ", ",
            "resultStructType = ", str(self.resultStructType), ", ",
            "annotations = ", str(self.annotations), ", ",
            "paramBrand = ", str(self.paramBrand), ", ",
            "resultBrand = ", str(self.resultBrand), ", ",
            "implicitParameters = ", str(self.implicitParameters), 
            ")"
            ]
        return "".join(parts)


@Enumerant.__extend__
class Enumerant(_Struct):
    __static_data_size__ = 1
    __static_ptrs_size__ = 2
    
    
    @property
    def name(self):
        # no union check
        return self._read_str_text(0)
    
    def has_name(self):
        offset, ptr = self._read_ptr(0)
        return ptr != 0
    
    @property
    def codeOrder(self):
        # no union check
        value = self._read_data(0, ord('H'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @property
    def annotations(self):
        # no union check
        return self._read_list(8, _StructList, Annotation)
    
    def has_annotations(self):
        offset, ptr = self._read_ptr(8)
        return ptr != 0
    
    @staticmethod
    def __new(name, codeOrder, annotations):
        builder = _StructBuilder('Hxxxxxxqq')
        name = builder.alloc_string(8, name)
        annotations = builder.alloc_list(16, _StructList, Annotation, annotations)
        buf = builder.build(codeOrder, name, annotations)
        return buf
    
    def __init__(self, name, codeOrder, annotations):
        buf = self.__new(name, codeOrder, annotations)
        _Struct.__init__(self, buf, 0, 1, 2)
    
    def shortrepr(self):
        parts = [
            "(",
            "name = ", str(self.name), ", ",
            "codeOrder = ", str(self.codeOrder), ", ",
            "annotations = ", str(self.annotations), 
            ")"
            ]
        return "".join(parts)


@Type_anyPointer_parameter.__extend__
class Type_anyPointer_parameter(_Struct):
    __static_data_size__ = 3
    __static_ptrs_size__ = 1
    
    
    @property
    def scopeId(self):
        # no union check
        value = self._read_data(16, ord('Q'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @property
    def parameterIndex(self):
        # no union check
        value = self._read_data(10, ord('H'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @staticmethod
    def __new(scopeId, parameterIndex):
        builder = _StructBuilder('xxxxxxxxxxHxxxxQxxxxxxxx')
        buf = builder.build(parameterIndex, scopeId)
        return buf
    
    def __init__(self, scopeId, parameterIndex):
        buf = self.__new(scopeId, parameterIndex)
        _Struct.__init__(self, buf, 0, 3, 1)
    
    def shortrepr(self):
        parts = [
            "(",
            "scopeId = ", str(self.scopeId), ", ",
            "parameterIndex = ", str(self.parameterIndex), 
            ")"
            ]
        return "".join(parts)


@Type_anyPointer_implicitMethodParameter.__extend__
class Type_anyPointer_implicitMethodParameter(_Struct):
    __static_data_size__ = 3
    __static_ptrs_size__ = 1
    
    
    @property
    def parameterIndex(self):
        # no union check
        value = self._read_data(10, ord('H'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @staticmethod
    def __new(parameterIndex):
        builder = _StructBuilder('xxxxxxxxxxHxxxxxxxxxxxxxxxxxxxx')
        buf = builder.build(parameterIndex)
        return buf
    
    def __init__(self, parameterIndex):
        buf = self.__new(parameterIndex)
        _Struct.__init__(self, buf, 0, 3, 1)
    
    def shortrepr(self):
        parts = [
            "(",
            "parameterIndex = ", str(self.parameterIndex), 
            ")"
            ]
        return "".join(parts)


@Type_anyPointer.__extend__
class Type_anyPointer(_Struct):
    __static_data_size__ = 3
    __static_ptrs_size__ = 1
    
    
    __tag_offset__ = 8
    __tag__ = _enum('anyPointer.__tag__', ('unconstrained', 'parameter', 'implicitMethodParameter'))
    
    @property
    def unconstrained(self):
        self._ensure_union(0)
        return None
    
    @property
    def parameter(self):
        self._ensure_union(1)
        return self._read_group(Type_anyPointer_parameter)
    
    @property
    def implicitMethodParameter(self):
        self._ensure_union(2)
        return self._read_group(Type_anyPointer_implicitMethodParameter)
    
    @staticmethod
    def __new_unconstrained():
        builder = _StructBuilder('xxxxxxxxhxxxxxxxxxxxxxxxxxxxxxx')
        __which__ = 0
        buf = builder.build(__which__)
        return buf
    @classmethod
    def new_unconstrained(cls):
        buf = cls.__new_unconstrained()
        return cls.from_buffer(buf, 0, 3, 1)
    
    @staticmethod
    def __new_parameter(*args, **kwargs):
        raise NotImplementedError('Group fields not supported yet')
    @classmethod
    def new_parameter(cls, *args):
        buf = cls.__new_parameter(*args)
        return cls.from_buffer(buf, 0, 3, 1)
    
    @staticmethod
    def __new_implicitMethodParameter(*args, **kwargs):
        raise NotImplementedError('Group fields not supported yet')
    @classmethod
    def new_implicitMethodParameter(cls, *args):
        buf = cls.__new_implicitMethodParameter(*args)
        return cls.from_buffer(buf, 0, 3, 1)
    
    def __init__(self, unconstrained=_undefined, parameter=_undefined, implicitMethodParameter=_undefined):
        if unconstrained is not _undefined:
            self._assert_undefined(parameter, "parameter", "unconstrained")
            self._assert_undefined(implicitMethodParameter, "implicitMethodParameter", "unconstrained")
            buf = self.__new_unconstrained(unconstrained=unconstrained)
            _Struct.__init__(self, buf, 0, 3, 1)
            return
        if parameter is not _undefined:
            self._assert_undefined(unconstrained, "unconstrained", "parameter")
            self._assert_undefined(implicitMethodParameter, "implicitMethodParameter", "parameter")
            buf = self.__new_parameter(parameter=parameter)
            _Struct.__init__(self, buf, 0, 3, 1)
            return
        if implicitMethodParameter is not _undefined:
            self._assert_undefined(unconstrained, "unconstrained", "implicitMethodParameter")
            self._assert_undefined(parameter, "parameter", "implicitMethodParameter")
            buf = self.__new_implicitMethodParameter(implicitMethodParameter=implicitMethodParameter)
            _Struct.__init__(self, buf, 0, 3, 1)
            return
        raise TypeError("one of the following args is required: unconstrained, parameter, implicitMethodParameter")
    
    def shortrepr(self):
        parts = [
            "(",
            "unconstrained = ", str(self.unconstrained), ", ",
            "parameter = ", str(self.parameter), ", ",
            "implicitMethodParameter = ", str(self.implicitMethodParameter), 
            ")"
            ]
        return "".join(parts)


@Type_struct.__extend__
class Type_struct(_Struct):
    __static_data_size__ = 3
    __static_ptrs_size__ = 1
    
    
    @property
    def typeId(self):
        # no union check
        value = self._read_data(8, ord('Q'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @property
    def brand(self):
        # no union check
        return self._read_struct(0, Brand)
    
    def has_brand(self):
        offset, ptr = self._read_ptr(0)
        return ptr != 0
    
    @staticmethod
    def __new(typeId, brand):
        builder = _StructBuilder('xxxxxxxxQxxxxxxxxq')
        brand = builder.alloc_struct(24, Brand, brand)
        buf = builder.build(typeId, brand)
        return buf
    
    def __init__(self, typeId, brand):
        buf = self.__new(typeId, brand)
        _Struct.__init__(self, buf, 0, 3, 1)
    
    def shortrepr(self):
        parts = [
            "(",
            "typeId = ", str(self.typeId), ", ",
            "brand = ", str(self.brand), 
            ")"
            ]
        return "".join(parts)


@Type_enum.__extend__
class Type_enum(_Struct):
    __static_data_size__ = 3
    __static_ptrs_size__ = 1
    
    
    @property
    def typeId(self):
        # no union check
        value = self._read_data(8, ord('Q'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @property
    def brand(self):
        # no union check
        return self._read_struct(0, Brand)
    
    def has_brand(self):
        offset, ptr = self._read_ptr(0)
        return ptr != 0
    
    @staticmethod
    def __new(typeId, brand):
        builder = _StructBuilder('xxxxxxxxQxxxxxxxxq')
        brand = builder.alloc_struct(24, Brand, brand)
        buf = builder.build(typeId, brand)
        return buf
    
    def __init__(self, typeId, brand):
        buf = self.__new(typeId, brand)
        _Struct.__init__(self, buf, 0, 3, 1)
    
    def shortrepr(self):
        parts = [
            "(",
            "typeId = ", str(self.typeId), ", ",
            "brand = ", str(self.brand), 
            ")"
            ]
        return "".join(parts)


@Type_interface.__extend__
class Type_interface(_Struct):
    __static_data_size__ = 3
    __static_ptrs_size__ = 1
    
    
    @property
    def typeId(self):
        # no union check
        value = self._read_data(8, ord('Q'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @property
    def brand(self):
        # no union check
        return self._read_struct(0, Brand)
    
    def has_brand(self):
        offset, ptr = self._read_ptr(0)
        return ptr != 0
    
    @staticmethod
    def __new(typeId, brand):
        builder = _StructBuilder('xxxxxxxxQxxxxxxxxq')
        brand = builder.alloc_struct(24, Brand, brand)
        buf = builder.build(typeId, brand)
        return buf
    
    def __init__(self, typeId, brand):
        buf = self.__new(typeId, brand)
        _Struct.__init__(self, buf, 0, 3, 1)
    
    def shortrepr(self):
        parts = [
            "(",
            "typeId = ", str(self.typeId), ", ",
            "brand = ", str(self.brand), 
            ")"
            ]
        return "".join(parts)


@Type_list.__extend__
class Type_list(_Struct):
    __static_data_size__ = 3
    __static_ptrs_size__ = 1
    
    
    @property
    def elementType(self):
        # no union check
        return self._read_struct(0, Type)
    
    def has_elementType(self):
        offset, ptr = self._read_ptr(0)
        return ptr != 0
    
    @staticmethod
    def __new(elementType):
        builder = _StructBuilder('xxxxxxxxxxxxxxxxxxxxxxxxq')
        elementType = builder.alloc_struct(24, Type, elementType)
        buf = builder.build(elementType)
        return buf
    
    def __init__(self, elementType):
        buf = self.__new(elementType)
        _Struct.__init__(self, buf, 0, 3, 1)
    
    def shortrepr(self):
        parts = [
            "(",
            "elementType = ", str(self.elementType), 
            ")"
            ]
        return "".join(parts)


@Type.__extend__
class Type(_Struct):
    __static_data_size__ = 3
    __static_ptrs_size__ = 1
    
    
    __tag_offset__ = 0
    __tag__ = _enum('Type.__tag__', ('void', 'bool', 'int8', 'int16', 'int32', 'int64', 'uint8', 'uint16', 'uint32', 'uint64', 'float32', 'float64', 'text', 'data', 'list', 'enum', 'struct', 'interface', 'anyPointer'))
    
    @property
    def void(self):
        self._ensure_union(0)
        return None
    
    @property
    def bool(self):
        self._ensure_union(1)
        return None
    
    @property
    def int8(self):
        self._ensure_union(2)
        return None
    
    @property
    def int16(self):
        self._ensure_union(3)
        return None
    
    @property
    def int32(self):
        self._ensure_union(4)
        return None
    
    @property
    def int64(self):
        self._ensure_union(5)
        return None
    
    @property
    def uint8(self):
        self._ensure_union(6)
        return None
    
    @property
    def uint16(self):
        self._ensure_union(7)
        return None
    
    @property
    def uint32(self):
        self._ensure_union(8)
        return None
    
    @property
    def uint64(self):
        self._ensure_union(9)
        return None
    
    @property
    def float32(self):
        self._ensure_union(10)
        return None
    
    @property
    def float64(self):
        self._ensure_union(11)
        return None
    
    @property
    def text(self):
        self._ensure_union(12)
        return None
    
    @property
    def data(self):
        self._ensure_union(13)
        return None
    
    @property
    def list(self):
        self._ensure_union(14)
        return self._read_group(Type_list)
    
    @property
    def enum(self):
        self._ensure_union(15)
        return self._read_group(Type_enum)
    
    @property
    def struct(self):
        self._ensure_union(16)
        return self._read_group(Type_struct)
    
    @property
    def interface(self):
        self._ensure_union(17)
        return self._read_group(Type_interface)
    
    @property
    def anyPointer(self):
        self._ensure_union(18)
        return self._read_group(Type_anyPointer)
    
    @staticmethod
    def __new_void():
        builder = _StructBuilder('hxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        __which__ = 0
        buf = builder.build(__which__)
        return buf
    @classmethod
    def new_void(cls):
        buf = cls.__new_void()
        return cls.from_buffer(buf, 0, 3, 1)
    
    @staticmethod
    def __new_bool():
        builder = _StructBuilder('hxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        __which__ = 1
        buf = builder.build(__which__)
        return buf
    @classmethod
    def new_bool(cls):
        buf = cls.__new_bool()
        return cls.from_buffer(buf, 0, 3, 1)
    
    @staticmethod
    def __new_int8():
        builder = _StructBuilder('hxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        __which__ = 2
        buf = builder.build(__which__)
        return buf
    @classmethod
    def new_int8(cls):
        buf = cls.__new_int8()
        return cls.from_buffer(buf, 0, 3, 1)
    
    @staticmethod
    def __new_int16():
        builder = _StructBuilder('hxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        __which__ = 3
        buf = builder.build(__which__)
        return buf
    @classmethod
    def new_int16(cls):
        buf = cls.__new_int16()
        return cls.from_buffer(buf, 0, 3, 1)
    
    @staticmethod
    def __new_int32():
        builder = _StructBuilder('hxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        __which__ = 4
        buf = builder.build(__which__)
        return buf
    @classmethod
    def new_int32(cls):
        buf = cls.__new_int32()
        return cls.from_buffer(buf, 0, 3, 1)
    
    @staticmethod
    def __new_int64():
        builder = _StructBuilder('hxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        __which__ = 5
        buf = builder.build(__which__)
        return buf
    @classmethod
    def new_int64(cls):
        buf = cls.__new_int64()
        return cls.from_buffer(buf, 0, 3, 1)
    
    @staticmethod
    def __new_uint8():
        builder = _StructBuilder('hxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        __which__ = 6
        buf = builder.build(__which__)
        return buf
    @classmethod
    def new_uint8(cls):
        buf = cls.__new_uint8()
        return cls.from_buffer(buf, 0, 3, 1)
    
    @staticmethod
    def __new_uint16():
        builder = _StructBuilder('hxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        __which__ = 7
        buf = builder.build(__which__)
        return buf
    @classmethod
    def new_uint16(cls):
        buf = cls.__new_uint16()
        return cls.from_buffer(buf, 0, 3, 1)
    
    @staticmethod
    def __new_uint32():
        builder = _StructBuilder('hxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        __which__ = 8
        buf = builder.build(__which__)
        return buf
    @classmethod
    def new_uint32(cls):
        buf = cls.__new_uint32()
        return cls.from_buffer(buf, 0, 3, 1)
    
    @staticmethod
    def __new_uint64():
        builder = _StructBuilder('hxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        __which__ = 9
        buf = builder.build(__which__)
        return buf
    @classmethod
    def new_uint64(cls):
        buf = cls.__new_uint64()
        return cls.from_buffer(buf, 0, 3, 1)
    
    @staticmethod
    def __new_float32():
        builder = _StructBuilder('hxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        __which__ = 10
        buf = builder.build(__which__)
        return buf
    @classmethod
    def new_float32(cls):
        buf = cls.__new_float32()
        return cls.from_buffer(buf, 0, 3, 1)
    
    @staticmethod
    def __new_float64():
        builder = _StructBuilder('hxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        __which__ = 11
        buf = builder.build(__which__)
        return buf
    @classmethod
    def new_float64(cls):
        buf = cls.__new_float64()
        return cls.from_buffer(buf, 0, 3, 1)
    
    @staticmethod
    def __new_text():
        builder = _StructBuilder('hxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        __which__ = 12
        buf = builder.build(__which__)
        return buf
    @classmethod
    def new_text(cls):
        buf = cls.__new_text()
        return cls.from_buffer(buf, 0, 3, 1)
    
    @staticmethod
    def __new_data():
        builder = _StructBuilder('hxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        __which__ = 13
        buf = builder.build(__which__)
        return buf
    @classmethod
    def new_data(cls):
        buf = cls.__new_data()
        return cls.from_buffer(buf, 0, 3, 1)
    
    @staticmethod
    def __new_list(*args, **kwargs):
        raise NotImplementedError('Group fields not supported yet')
    @classmethod
    def new_list(cls, *args):
        buf = cls.__new_list(*args)
        return cls.from_buffer(buf, 0, 3, 1)
    
    @staticmethod
    def __new_enum(*args, **kwargs):
        raise NotImplementedError('Group fields not supported yet')
    @classmethod
    def new_enum(cls, *args):
        buf = cls.__new_enum(*args)
        return cls.from_buffer(buf, 0, 3, 1)
    
    @staticmethod
    def __new_struct(*args, **kwargs):
        raise NotImplementedError('Group fields not supported yet')
    @classmethod
    def new_struct(cls, *args):
        buf = cls.__new_struct(*args)
        return cls.from_buffer(buf, 0, 3, 1)
    
    @staticmethod
    def __new_interface(*args, **kwargs):
        raise NotImplementedError('Group fields not supported yet')
    @classmethod
    def new_interface(cls, *args):
        buf = cls.__new_interface(*args)
        return cls.from_buffer(buf, 0, 3, 1)
    
    @staticmethod
    def __new_anyPointer(*args, **kwargs):
        raise NotImplementedError('Group fields not supported yet')
    @classmethod
    def new_anyPointer(cls, *args):
        buf = cls.__new_anyPointer(*args)
        return cls.from_buffer(buf, 0, 3, 1)
    
    def __init__(self, void=_undefined, bool=_undefined, int8=_undefined, int16=_undefined, int32=_undefined, int64=_undefined, uint8=_undefined, uint16=_undefined, uint32=_undefined, uint64=_undefined, float32=_undefined, float64=_undefined, text=_undefined, data=_undefined, list=_undefined, enum=_undefined, struct=_undefined, interface=_undefined, anyPointer=_undefined):
        if void is not _undefined:
            self._assert_undefined(bool, "bool", "void")
            self._assert_undefined(int8, "int8", "void")
            self._assert_undefined(int16, "int16", "void")
            self._assert_undefined(int32, "int32", "void")
            self._assert_undefined(int64, "int64", "void")
            self._assert_undefined(uint8, "uint8", "void")
            self._assert_undefined(uint16, "uint16", "void")
            self._assert_undefined(uint32, "uint32", "void")
            self._assert_undefined(uint64, "uint64", "void")
            self._assert_undefined(float32, "float32", "void")
            self._assert_undefined(float64, "float64", "void")
            self._assert_undefined(text, "text", "void")
            self._assert_undefined(data, "data", "void")
            self._assert_undefined(list, "list", "void")
            self._assert_undefined(enum, "enum", "void")
            self._assert_undefined(struct, "struct", "void")
            self._assert_undefined(interface, "interface", "void")
            self._assert_undefined(anyPointer, "anyPointer", "void")
            buf = self.__new_void(void=void)
            _Struct.__init__(self, buf, 0, 3, 1)
            return
        if bool is not _undefined:
            self._assert_undefined(void, "void", "bool")
            self._assert_undefined(int8, "int8", "bool")
            self._assert_undefined(int16, "int16", "bool")
            self._assert_undefined(int32, "int32", "bool")
            self._assert_undefined(int64, "int64", "bool")
            self._assert_undefined(uint8, "uint8", "bool")
            self._assert_undefined(uint16, "uint16", "bool")
            self._assert_undefined(uint32, "uint32", "bool")
            self._assert_undefined(uint64, "uint64", "bool")
            self._assert_undefined(float32, "float32", "bool")
            self._assert_undefined(float64, "float64", "bool")
            self._assert_undefined(text, "text", "bool")
            self._assert_undefined(data, "data", "bool")
            self._assert_undefined(list, "list", "bool")
            self._assert_undefined(enum, "enum", "bool")
            self._assert_undefined(struct, "struct", "bool")
            self._assert_undefined(interface, "interface", "bool")
            self._assert_undefined(anyPointer, "anyPointer", "bool")
            buf = self.__new_bool(bool=bool)
            _Struct.__init__(self, buf, 0, 3, 1)
            return
        if int8 is not _undefined:
            self._assert_undefined(void, "void", "int8")
            self._assert_undefined(bool, "bool", "int8")
            self._assert_undefined(int16, "int16", "int8")
            self._assert_undefined(int32, "int32", "int8")
            self._assert_undefined(int64, "int64", "int8")
            self._assert_undefined(uint8, "uint8", "int8")
            self._assert_undefined(uint16, "uint16", "int8")
            self._assert_undefined(uint32, "uint32", "int8")
            self._assert_undefined(uint64, "uint64", "int8")
            self._assert_undefined(float32, "float32", "int8")
            self._assert_undefined(float64, "float64", "int8")
            self._assert_undefined(text, "text", "int8")
            self._assert_undefined(data, "data", "int8")
            self._assert_undefined(list, "list", "int8")
            self._assert_undefined(enum, "enum", "int8")
            self._assert_undefined(struct, "struct", "int8")
            self._assert_undefined(interface, "interface", "int8")
            self._assert_undefined(anyPointer, "anyPointer", "int8")
            buf = self.__new_int8(int8=int8)
            _Struct.__init__(self, buf, 0, 3, 1)
            return
        if int16 is not _undefined:
            self._assert_undefined(void, "void", "int16")
            self._assert_undefined(bool, "bool", "int16")
            self._assert_undefined(int8, "int8", "int16")
            self._assert_undefined(int32, "int32", "int16")
            self._assert_undefined(int64, "int64", "int16")
            self._assert_undefined(uint8, "uint8", "int16")
            self._assert_undefined(uint16, "uint16", "int16")
            self._assert_undefined(uint32, "uint32", "int16")
            self._assert_undefined(uint64, "uint64", "int16")
            self._assert_undefined(float32, "float32", "int16")
            self._assert_undefined(float64, "float64", "int16")
            self._assert_undefined(text, "text", "int16")
            self._assert_undefined(data, "data", "int16")
            self._assert_undefined(list, "list", "int16")
            self._assert_undefined(enum, "enum", "int16")
            self._assert_undefined(struct, "struct", "int16")
            self._assert_undefined(interface, "interface", "int16")
            self._assert_undefined(anyPointer, "anyPointer", "int16")
            buf = self.__new_int16(int16=int16)
            _Struct.__init__(self, buf, 0, 3, 1)
            return
        if int32 is not _undefined:
            self._assert_undefined(void, "void", "int32")
            self._assert_undefined(bool, "bool", "int32")
            self._assert_undefined(int8, "int8", "int32")
            self._assert_undefined(int16, "int16", "int32")
            self._assert_undefined(int64, "int64", "int32")
            self._assert_undefined(uint8, "uint8", "int32")
            self._assert_undefined(uint16, "uint16", "int32")
            self._assert_undefined(uint32, "uint32", "int32")
            self._assert_undefined(uint64, "uint64", "int32")
            self._assert_undefined(float32, "float32", "int32")
            self._assert_undefined(float64, "float64", "int32")
            self._assert_undefined(text, "text", "int32")
            self._assert_undefined(data, "data", "int32")
            self._assert_undefined(list, "list", "int32")
            self._assert_undefined(enum, "enum", "int32")
            self._assert_undefined(struct, "struct", "int32")
            self._assert_undefined(interface, "interface", "int32")
            self._assert_undefined(anyPointer, "anyPointer", "int32")
            buf = self.__new_int32(int32=int32)
            _Struct.__init__(self, buf, 0, 3, 1)
            return
        if int64 is not _undefined:
            self._assert_undefined(void, "void", "int64")
            self._assert_undefined(bool, "bool", "int64")
            self._assert_undefined(int8, "int8", "int64")
            self._assert_undefined(int16, "int16", "int64")
            self._assert_undefined(int32, "int32", "int64")
            self._assert_undefined(uint8, "uint8", "int64")
            self._assert_undefined(uint16, "uint16", "int64")
            self._assert_undefined(uint32, "uint32", "int64")
            self._assert_undefined(uint64, "uint64", "int64")
            self._assert_undefined(float32, "float32", "int64")
            self._assert_undefined(float64, "float64", "int64")
            self._assert_undefined(text, "text", "int64")
            self._assert_undefined(data, "data", "int64")
            self._assert_undefined(list, "list", "int64")
            self._assert_undefined(enum, "enum", "int64")
            self._assert_undefined(struct, "struct", "int64")
            self._assert_undefined(interface, "interface", "int64")
            self._assert_undefined(anyPointer, "anyPointer", "int64")
            buf = self.__new_int64(int64=int64)
            _Struct.__init__(self, buf, 0, 3, 1)
            return
        if uint8 is not _undefined:
            self._assert_undefined(void, "void", "uint8")
            self._assert_undefined(bool, "bool", "uint8")
            self._assert_undefined(int8, "int8", "uint8")
            self._assert_undefined(int16, "int16", "uint8")
            self._assert_undefined(int32, "int32", "uint8")
            self._assert_undefined(int64, "int64", "uint8")
            self._assert_undefined(uint16, "uint16", "uint8")
            self._assert_undefined(uint32, "uint32", "uint8")
            self._assert_undefined(uint64, "uint64", "uint8")
            self._assert_undefined(float32, "float32", "uint8")
            self._assert_undefined(float64, "float64", "uint8")
            self._assert_undefined(text, "text", "uint8")
            self._assert_undefined(data, "data", "uint8")
            self._assert_undefined(list, "list", "uint8")
            self._assert_undefined(enum, "enum", "uint8")
            self._assert_undefined(struct, "struct", "uint8")
            self._assert_undefined(interface, "interface", "uint8")
            self._assert_undefined(anyPointer, "anyPointer", "uint8")
            buf = self.__new_uint8(uint8=uint8)
            _Struct.__init__(self, buf, 0, 3, 1)
            return
        if uint16 is not _undefined:
            self._assert_undefined(void, "void", "uint16")
            self._assert_undefined(bool, "bool", "uint16")
            self._assert_undefined(int8, "int8", "uint16")
            self._assert_undefined(int16, "int16", "uint16")
            self._assert_undefined(int32, "int32", "uint16")
            self._assert_undefined(int64, "int64", "uint16")
            self._assert_undefined(uint8, "uint8", "uint16")
            self._assert_undefined(uint32, "uint32", "uint16")
            self._assert_undefined(uint64, "uint64", "uint16")
            self._assert_undefined(float32, "float32", "uint16")
            self._assert_undefined(float64, "float64", "uint16")
            self._assert_undefined(text, "text", "uint16")
            self._assert_undefined(data, "data", "uint16")
            self._assert_undefined(list, "list", "uint16")
            self._assert_undefined(enum, "enum", "uint16")
            self._assert_undefined(struct, "struct", "uint16")
            self._assert_undefined(interface, "interface", "uint16")
            self._assert_undefined(anyPointer, "anyPointer", "uint16")
            buf = self.__new_uint16(uint16=uint16)
            _Struct.__init__(self, buf, 0, 3, 1)
            return
        if uint32 is not _undefined:
            self._assert_undefined(void, "void", "uint32")
            self._assert_undefined(bool, "bool", "uint32")
            self._assert_undefined(int8, "int8", "uint32")
            self._assert_undefined(int16, "int16", "uint32")
            self._assert_undefined(int32, "int32", "uint32")
            self._assert_undefined(int64, "int64", "uint32")
            self._assert_undefined(uint8, "uint8", "uint32")
            self._assert_undefined(uint16, "uint16", "uint32")
            self._assert_undefined(uint64, "uint64", "uint32")
            self._assert_undefined(float32, "float32", "uint32")
            self._assert_undefined(float64, "float64", "uint32")
            self._assert_undefined(text, "text", "uint32")
            self._assert_undefined(data, "data", "uint32")
            self._assert_undefined(list, "list", "uint32")
            self._assert_undefined(enum, "enum", "uint32")
            self._assert_undefined(struct, "struct", "uint32")
            self._assert_undefined(interface, "interface", "uint32")
            self._assert_undefined(anyPointer, "anyPointer", "uint32")
            buf = self.__new_uint32(uint32=uint32)
            _Struct.__init__(self, buf, 0, 3, 1)
            return
        if uint64 is not _undefined:
            self._assert_undefined(void, "void", "uint64")
            self._assert_undefined(bool, "bool", "uint64")
            self._assert_undefined(int8, "int8", "uint64")
            self._assert_undefined(int16, "int16", "uint64")
            self._assert_undefined(int32, "int32", "uint64")
            self._assert_undefined(int64, "int64", "uint64")
            self._assert_undefined(uint8, "uint8", "uint64")
            self._assert_undefined(uint16, "uint16", "uint64")
            self._assert_undefined(uint32, "uint32", "uint64")
            self._assert_undefined(float32, "float32", "uint64")
            self._assert_undefined(float64, "float64", "uint64")
            self._assert_undefined(text, "text", "uint64")
            self._assert_undefined(data, "data", "uint64")
            self._assert_undefined(list, "list", "uint64")
            self._assert_undefined(enum, "enum", "uint64")
            self._assert_undefined(struct, "struct", "uint64")
            self._assert_undefined(interface, "interface", "uint64")
            self._assert_undefined(anyPointer, "anyPointer", "uint64")
            buf = self.__new_uint64(uint64=uint64)
            _Struct.__init__(self, buf, 0, 3, 1)
            return
        if float32 is not _undefined:
            self._assert_undefined(void, "void", "float32")
            self._assert_undefined(bool, "bool", "float32")
            self._assert_undefined(int8, "int8", "float32")
            self._assert_undefined(int16, "int16", "float32")
            self._assert_undefined(int32, "int32", "float32")
            self._assert_undefined(int64, "int64", "float32")
            self._assert_undefined(uint8, "uint8", "float32")
            self._assert_undefined(uint16, "uint16", "float32")
            self._assert_undefined(uint32, "uint32", "float32")
            self._assert_undefined(uint64, "uint64", "float32")
            self._assert_undefined(float64, "float64", "float32")
            self._assert_undefined(text, "text", "float32")
            self._assert_undefined(data, "data", "float32")
            self._assert_undefined(list, "list", "float32")
            self._assert_undefined(enum, "enum", "float32")
            self._assert_undefined(struct, "struct", "float32")
            self._assert_undefined(interface, "interface", "float32")
            self._assert_undefined(anyPointer, "anyPointer", "float32")
            buf = self.__new_float32(float32=float32)
            _Struct.__init__(self, buf, 0, 3, 1)
            return
        if float64 is not _undefined:
            self._assert_undefined(void, "void", "float64")
            self._assert_undefined(bool, "bool", "float64")
            self._assert_undefined(int8, "int8", "float64")
            self._assert_undefined(int16, "int16", "float64")
            self._assert_undefined(int32, "int32", "float64")
            self._assert_undefined(int64, "int64", "float64")
            self._assert_undefined(uint8, "uint8", "float64")
            self._assert_undefined(uint16, "uint16", "float64")
            self._assert_undefined(uint32, "uint32", "float64")
            self._assert_undefined(uint64, "uint64", "float64")
            self._assert_undefined(float32, "float32", "float64")
            self._assert_undefined(text, "text", "float64")
            self._assert_undefined(data, "data", "float64")
            self._assert_undefined(list, "list", "float64")
            self._assert_undefined(enum, "enum", "float64")
            self._assert_undefined(struct, "struct", "float64")
            self._assert_undefined(interface, "interface", "float64")
            self._assert_undefined(anyPointer, "anyPointer", "float64")
            buf = self.__new_float64(float64=float64)
            _Struct.__init__(self, buf, 0, 3, 1)
            return
        if text is not _undefined:
            self._assert_undefined(void, "void", "text")
            self._assert_undefined(bool, "bool", "text")
            self._assert_undefined(int8, "int8", "text")
            self._assert_undefined(int16, "int16", "text")
            self._assert_undefined(int32, "int32", "text")
            self._assert_undefined(int64, "int64", "text")
            self._assert_undefined(uint8, "uint8", "text")
            self._assert_undefined(uint16, "uint16", "text")
            self._assert_undefined(uint32, "uint32", "text")
            self._assert_undefined(uint64, "uint64", "text")
            self._assert_undefined(float32, "float32", "text")
            self._assert_undefined(float64, "float64", "text")
            self._assert_undefined(data, "data", "text")
            self._assert_undefined(list, "list", "text")
            self._assert_undefined(enum, "enum", "text")
            self._assert_undefined(struct, "struct", "text")
            self._assert_undefined(interface, "interface", "text")
            self._assert_undefined(anyPointer, "anyPointer", "text")
            buf = self.__new_text(text=text)
            _Struct.__init__(self, buf, 0, 3, 1)
            return
        if data is not _undefined:
            self._assert_undefined(void, "void", "data")
            self._assert_undefined(bool, "bool", "data")
            self._assert_undefined(int8, "int8", "data")
            self._assert_undefined(int16, "int16", "data")
            self._assert_undefined(int32, "int32", "data")
            self._assert_undefined(int64, "int64", "data")
            self._assert_undefined(uint8, "uint8", "data")
            self._assert_undefined(uint16, "uint16", "data")
            self._assert_undefined(uint32, "uint32", "data")
            self._assert_undefined(uint64, "uint64", "data")
            self._assert_undefined(float32, "float32", "data")
            self._assert_undefined(float64, "float64", "data")
            self._assert_undefined(text, "text", "data")
            self._assert_undefined(list, "list", "data")
            self._assert_undefined(enum, "enum", "data")
            self._assert_undefined(struct, "struct", "data")
            self._assert_undefined(interface, "interface", "data")
            self._assert_undefined(anyPointer, "anyPointer", "data")
            buf = self.__new_data(data=data)
            _Struct.__init__(self, buf, 0, 3, 1)
            return
        if list is not _undefined:
            self._assert_undefined(void, "void", "list")
            self._assert_undefined(bool, "bool", "list")
            self._assert_undefined(int8, "int8", "list")
            self._assert_undefined(int16, "int16", "list")
            self._assert_undefined(int32, "int32", "list")
            self._assert_undefined(int64, "int64", "list")
            self._assert_undefined(uint8, "uint8", "list")
            self._assert_undefined(uint16, "uint16", "list")
            self._assert_undefined(uint32, "uint32", "list")
            self._assert_undefined(uint64, "uint64", "list")
            self._assert_undefined(float32, "float32", "list")
            self._assert_undefined(float64, "float64", "list")
            self._assert_undefined(text, "text", "list")
            self._assert_undefined(data, "data", "list")
            self._assert_undefined(enum, "enum", "list")
            self._assert_undefined(struct, "struct", "list")
            self._assert_undefined(interface, "interface", "list")
            self._assert_undefined(anyPointer, "anyPointer", "list")
            buf = self.__new_list(list=list)
            _Struct.__init__(self, buf, 0, 3, 1)
            return
        if enum is not _undefined:
            self._assert_undefined(void, "void", "enum")
            self._assert_undefined(bool, "bool", "enum")
            self._assert_undefined(int8, "int8", "enum")
            self._assert_undefined(int16, "int16", "enum")
            self._assert_undefined(int32, "int32", "enum")
            self._assert_undefined(int64, "int64", "enum")
            self._assert_undefined(uint8, "uint8", "enum")
            self._assert_undefined(uint16, "uint16", "enum")
            self._assert_undefined(uint32, "uint32", "enum")
            self._assert_undefined(uint64, "uint64", "enum")
            self._assert_undefined(float32, "float32", "enum")
            self._assert_undefined(float64, "float64", "enum")
            self._assert_undefined(text, "text", "enum")
            self._assert_undefined(data, "data", "enum")
            self._assert_undefined(list, "list", "enum")
            self._assert_undefined(struct, "struct", "enum")
            self._assert_undefined(interface, "interface", "enum")
            self._assert_undefined(anyPointer, "anyPointer", "enum")
            buf = self.__new_enum(enum=enum)
            _Struct.__init__(self, buf, 0, 3, 1)
            return
        if struct is not _undefined:
            self._assert_undefined(void, "void", "struct")
            self._assert_undefined(bool, "bool", "struct")
            self._assert_undefined(int8, "int8", "struct")
            self._assert_undefined(int16, "int16", "struct")
            self._assert_undefined(int32, "int32", "struct")
            self._assert_undefined(int64, "int64", "struct")
            self._assert_undefined(uint8, "uint8", "struct")
            self._assert_undefined(uint16, "uint16", "struct")
            self._assert_undefined(uint32, "uint32", "struct")
            self._assert_undefined(uint64, "uint64", "struct")
            self._assert_undefined(float32, "float32", "struct")
            self._assert_undefined(float64, "float64", "struct")
            self._assert_undefined(text, "text", "struct")
            self._assert_undefined(data, "data", "struct")
            self._assert_undefined(list, "list", "struct")
            self._assert_undefined(enum, "enum", "struct")
            self._assert_undefined(interface, "interface", "struct")
            self._assert_undefined(anyPointer, "anyPointer", "struct")
            buf = self.__new_struct(struct=struct)
            _Struct.__init__(self, buf, 0, 3, 1)
            return
        if interface is not _undefined:
            self._assert_undefined(void, "void", "interface")
            self._assert_undefined(bool, "bool", "interface")
            self._assert_undefined(int8, "int8", "interface")
            self._assert_undefined(int16, "int16", "interface")
            self._assert_undefined(int32, "int32", "interface")
            self._assert_undefined(int64, "int64", "interface")
            self._assert_undefined(uint8, "uint8", "interface")
            self._assert_undefined(uint16, "uint16", "interface")
            self._assert_undefined(uint32, "uint32", "interface")
            self._assert_undefined(uint64, "uint64", "interface")
            self._assert_undefined(float32, "float32", "interface")
            self._assert_undefined(float64, "float64", "interface")
            self._assert_undefined(text, "text", "interface")
            self._assert_undefined(data, "data", "interface")
            self._assert_undefined(list, "list", "interface")
            self._assert_undefined(enum, "enum", "interface")
            self._assert_undefined(struct, "struct", "interface")
            self._assert_undefined(anyPointer, "anyPointer", "interface")
            buf = self.__new_interface(interface=interface)
            _Struct.__init__(self, buf, 0, 3, 1)
            return
        if anyPointer is not _undefined:
            self._assert_undefined(void, "void", "anyPointer")
            self._assert_undefined(bool, "bool", "anyPointer")
            self._assert_undefined(int8, "int8", "anyPointer")
            self._assert_undefined(int16, "int16", "anyPointer")
            self._assert_undefined(int32, "int32", "anyPointer")
            self._assert_undefined(int64, "int64", "anyPointer")
            self._assert_undefined(uint8, "uint8", "anyPointer")
            self._assert_undefined(uint16, "uint16", "anyPointer")
            self._assert_undefined(uint32, "uint32", "anyPointer")
            self._assert_undefined(uint64, "uint64", "anyPointer")
            self._assert_undefined(float32, "float32", "anyPointer")
            self._assert_undefined(float64, "float64", "anyPointer")
            self._assert_undefined(text, "text", "anyPointer")
            self._assert_undefined(data, "data", "anyPointer")
            self._assert_undefined(list, "list", "anyPointer")
            self._assert_undefined(enum, "enum", "anyPointer")
            self._assert_undefined(struct, "struct", "anyPointer")
            self._assert_undefined(interface, "interface", "anyPointer")
            buf = self.__new_anyPointer(anyPointer=anyPointer)
            _Struct.__init__(self, buf, 0, 3, 1)
            return
        raise TypeError("one of the following args is required: void, bool, int8, int16, int32, int64, uint8, uint16, uint32, uint64, float32, float64, text, data, list, enum, struct, interface, anyPointer")
    
    def shortrepr(self):
        parts = [
            "(",
            "void = ", str(self.void), ", ",
            "bool = ", str(self.bool), ", ",
            "int8 = ", str(self.int8), ", ",
            "int16 = ", str(self.int16), ", ",
            "int32 = ", str(self.int32), ", ",
            "int64 = ", str(self.int64), ", ",
            "uint8 = ", str(self.uint8), ", ",
            "uint16 = ", str(self.uint16), ", ",
            "uint32 = ", str(self.uint32), ", ",
            "uint64 = ", str(self.uint64), ", ",
            "float32 = ", str(self.float32), ", ",
            "float64 = ", str(self.float64), ", ",
            "text = ", str(self.text), ", ",
            "data = ", str(self.data), ", ",
            "list = ", str(self.list), ", ",
            "enum = ", str(self.enum), ", ",
            "struct = ", str(self.struct), ", ",
            "interface = ", str(self.interface), ", ",
            "anyPointer = ", str(self.anyPointer), 
            ")"
            ]
        return "".join(parts)


@Field_group.__extend__
class Field_group(_Struct):
    __static_data_size__ = 3
    __static_ptrs_size__ = 4
    
    
    @property
    def typeId(self):
        # no union check
        value = self._read_data(16, ord('Q'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @staticmethod
    def __new(typeId):
        builder = _StructBuilder('xxxxxxxxxxxxxxxxQxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        buf = builder.build(typeId)
        return buf
    
    def __init__(self, typeId):
        buf = self.__new(typeId)
        _Struct.__init__(self, buf, 0, 3, 4)
    
    def shortrepr(self):
        parts = [
            "(",
            "typeId = ", str(self.typeId), 
            ")"
            ]
        return "".join(parts)


@Field_ordinal.__extend__
class Field_ordinal(_Struct):
    __static_data_size__ = 3
    __static_ptrs_size__ = 4
    
    
    __tag_offset__ = 10
    __tag__ = _enum('ordinal.__tag__', ('implicit', 'explicit'))
    
    @property
    def implicit(self):
        self._ensure_union(0)
        return None
    
    @property
    def explicit(self):
        self._ensure_union(1)
        value = self._read_data(12, ord('H'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @staticmethod
    def __new_implicit():
        builder = _StructBuilder('xxxxxxxxxxhxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        __which__ = 0
        buf = builder.build(__which__)
        return buf
    @classmethod
    def new_implicit(cls):
        buf = cls.__new_implicit()
        return cls.from_buffer(buf, 0, 3, 4)
    
    @staticmethod
    def __new_explicit(explicit):
        builder = _StructBuilder('xxxxxxxxxxhHxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        __which__ = 1
        buf = builder.build(__which__, explicit)
        return buf
    @classmethod
    def new_explicit(cls, explicit):
        buf = cls.__new_explicit(explicit)
        return cls.from_buffer(buf, 0, 3, 4)
    
    def __init__(self, implicit=_undefined, explicit=_undefined):
        if implicit is not _undefined:
            self._assert_undefined(explicit, "explicit", "implicit")
            buf = self.__new_implicit(implicit=implicit)
            _Struct.__init__(self, buf, 0, 3, 4)
            return
        if explicit is not _undefined:
            self._assert_undefined(implicit, "implicit", "explicit")
            buf = self.__new_explicit(explicit=explicit)
            _Struct.__init__(self, buf, 0, 3, 4)
            return
        raise TypeError("one of the following args is required: implicit, explicit")
    
    def shortrepr(self):
        parts = [
            "(",
            "implicit = ", str(self.implicit), ", ",
            "explicit = ", str(self.explicit), 
            ")"
            ]
        return "".join(parts)


@Field_slot.__extend__
class Field_slot(_Struct):
    __static_data_size__ = 3
    __static_ptrs_size__ = 4
    
    
    @property
    def offset(self):
        # no union check
        value = self._read_data(4, ord('I'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @property
    def type(self):
        # no union check
        return self._read_struct(16, Type)
    
    def has_type(self):
        offset, ptr = self._read_ptr(16)
        return ptr != 0
    
    @property
    def defaultValue(self):
        # no union check
        return self._read_struct(24, Value)
    
    def has_defaultValue(self):
        offset, ptr = self._read_ptr(24)
        return ptr != 0
    
    @property
    def hadExplicitDefault(self):
        # no union check
        value = self._read_bit(16, 1)
        if False != 0:
            value = value ^ False
        return value
    
    @staticmethod
    def __new(*args, **kwargs):
        raise NotImplementedError('Unsupported field type: <capnpy.schema_extended.Field__Slot object at 0x7f43ada39830>')
    
    def __init__(self, *args):
        buf = self.__new(*args)
        _Struct.__init__(self, buf, 0, 3, 4)
    
    def shortrepr(self):
        parts = [
            "(",
            "offset = ", str(self.offset), ", ",
            "type = ", str(self.type), ", ",
            "defaultValue = ", str(self.defaultValue), ", ",
            "hadExplicitDefault = ", str(self.hadExplicitDefault), 
            ")"
            ]
        return "".join(parts)


@Field.__extend__
class Field(_Struct):
    __static_data_size__ = 3
    __static_ptrs_size__ = 4
    
    noDiscriminant = 65535
    
    __tag_offset__ = 8
    __tag__ = _enum('Field.__tag__', ('slot', 'group'))
    
    @property
    def name(self):
        # no union check
        return self._read_str_text(0)
    
    def has_name(self):
        offset, ptr = self._read_ptr(0)
        return ptr != 0
    
    @property
    def codeOrder(self):
        # no union check
        value = self._read_data(0, ord('H'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @property
    def annotations(self):
        # no union check
        return self._read_list(8, _StructList, Annotation)
    
    def has_annotations(self):
        offset, ptr = self._read_ptr(8)
        return ptr != 0
    
    @property
    def discriminantValue(self):
        # no union check
        value = self._read_data(2, ord('H'))
        if 65535 != 0:
            value = value ^ 65535
        return value
    
    @property
    def slot(self):
        self._ensure_union(0)
        return self._read_group(Field_slot)
    
    @property
    def group(self):
        self._ensure_union(1)
        return self._read_group(Field_group)
    
    @property
    def ordinal(self):
        # no union check
        return self._read_group(Field_ordinal)
    
    @staticmethod
    def __new_slot(*args, **kwargs):
        raise NotImplementedError('Group fields not supported yet')
    @classmethod
    def new_slot(cls, *args):
        buf = cls.__new_slot(*args)
        return cls.from_buffer(buf, 0, 3, 4)
    
    @staticmethod
    def __new_group(*args, **kwargs):
        raise NotImplementedError('Group fields not supported yet')
    @classmethod
    def new_group(cls, *args):
        buf = cls.__new_group(*args)
        return cls.from_buffer(buf, 0, 3, 4)
    
    def __init__(self, name, codeOrder, annotations, discriminantValue, ordinal, slot=_undefined, group=_undefined):
        if slot is not _undefined:
            self._assert_undefined(group, "group", "slot")
            buf = self.__new_slot(name=name, codeOrder=codeOrder, annotations=annotations, discriminantValue=discriminantValue, ordinal=ordinal, slot=slot)
            _Struct.__init__(self, buf, 0, 3, 4)
            return
        if group is not _undefined:
            self._assert_undefined(slot, "slot", "group")
            buf = self.__new_group(name=name, codeOrder=codeOrder, annotations=annotations, discriminantValue=discriminantValue, ordinal=ordinal, group=group)
            _Struct.__init__(self, buf, 0, 3, 4)
            return
        raise TypeError("one of the following args is required: slot, group")
    
    def shortrepr(self):
        parts = [
            "(",
            "name = ", str(self.name), ", ",
            "codeOrder = ", str(self.codeOrder), ", ",
            "annotations = ", str(self.annotations), ", ",
            "discriminantValue = ", str(self.discriminantValue), ", ",
            "slot = ", str(self.slot), ", ",
            "group = ", str(self.group), ", ",
            "ordinal = ", str(self.ordinal), 
            ")"
            ]
        return "".join(parts)


@Superclass.__extend__
class Superclass(_Struct):
    __static_data_size__ = 1
    __static_ptrs_size__ = 1
    
    
    @property
    def id(self):
        # no union check
        value = self._read_data(0, ord('Q'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @property
    def brand(self):
        # no union check
        return self._read_struct(0, Brand)
    
    def has_brand(self):
        offset, ptr = self._read_ptr(0)
        return ptr != 0
    
    @staticmethod
    def __new(id, brand):
        builder = _StructBuilder('Qq')
        brand = builder.alloc_struct(8, Brand, brand)
        buf = builder.build(id, brand)
        return buf
    
    def __init__(self, id, brand):
        buf = self.__new(id, brand)
        _Struct.__init__(self, buf, 0, 1, 1)
    
    def shortrepr(self):
        parts = [
            "(",
            "id = ", str(self.id), ", ",
            "brand = ", str(self.brand), 
            ")"
            ]
        return "".join(parts)


@Value.__extend__
class Value(_Struct):
    __static_data_size__ = 2
    __static_ptrs_size__ = 1
    
    
    __tag_offset__ = 0
    __tag__ = _enum('Value.__tag__', ('void', 'bool', 'int8', 'int16', 'int32', 'int64', 'uint8', 'uint16', 'uint32', 'uint64', 'float32', 'float64', 'text', 'data', 'list', 'enum', 'struct', 'interface', 'anyPointer'))
    
    @property
    def void(self):
        self._ensure_union(0)
        return None
    
    @property
    def bool(self):
        self._ensure_union(1)
        value = self._read_bit(2, 1)
        if False != 0:
            value = value ^ False
        return value
    
    @property
    def int8(self):
        self._ensure_union(2)
        value = self._read_data(2, ord('b'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @property
    def int16(self):
        self._ensure_union(3)
        value = self._read_data(2, ord('h'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @property
    def int32(self):
        self._ensure_union(4)
        value = self._read_data(4, ord('i'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @property
    def int64(self):
        self._ensure_union(5)
        value = self._read_data(8, ord('q'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @property
    def uint8(self):
        self._ensure_union(6)
        value = self._read_data(2, ord('B'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @property
    def uint16(self):
        self._ensure_union(7)
        value = self._read_data(2, ord('H'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @property
    def uint32(self):
        self._ensure_union(8)
        value = self._read_data(4, ord('I'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @property
    def uint64(self):
        self._ensure_union(9)
        value = self._read_data(8, ord('Q'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @property
    def float32(self):
        self._ensure_union(10)
        value = self._read_data(4, ord('f'))
        if 0.0 != 0:
            value = value ^ 0.0
        return value
    
    @property
    def float64(self):
        self._ensure_union(11)
        value = self._read_data(8, ord('d'))
        if 0.0 != 0:
            value = value ^ 0.0
        return value
    
    @property
    def text(self):
        self._ensure_union(12)
        return self._read_str_text(0)
    
    def has_text(self):
        offset, ptr = self._read_ptr(0)
        return ptr != 0
    
    @property
    def data(self):
        self._ensure_union(13)
        return self._read_str_data(0)
    
    def has_data(self):
        offset, ptr = self._read_ptr(0)
        return ptr != 0
    
    @property
    def list(self):
        self._ensure_union(14)
        raise ValueError("Cannot get fields of type AnyPointer")
    
    def has_list(self):
        offset, ptr = self._read_ptr(0)
        return ptr != 0
    
    @property
    def enum(self):
        self._ensure_union(15)
        value = self._read_data(2, ord('H'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @property
    def struct(self):
        self._ensure_union(16)
        raise ValueError("Cannot get fields of type AnyPointer")
    
    def has_struct(self):
        offset, ptr = self._read_ptr(0)
        return ptr != 0
    
    @property
    def interface(self):
        self._ensure_union(17)
        return None
    
    @property
    def anyPointer(self):
        self._ensure_union(18)
        raise ValueError("Cannot get fields of type AnyPointer")
    
    def has_anyPointer(self):
        offset, ptr = self._read_ptr(0)
        return ptr != 0
    
    @staticmethod
    def __new_void():
        builder = _StructBuilder('hxxxxxxxxxxxxxxxxxxxxxx')
        __which__ = 0
        buf = builder.build(__which__)
        return buf
    @classmethod
    def new_void(cls):
        buf = cls.__new_void()
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_bool(*args, **kwargs):
        raise NotImplementedError('Unsupported field type: <capnpy.schema_extended.Field__Slot object at 0x7f43ada39520>')
    @classmethod
    def new_bool(cls, *args):
        buf = cls.__new_bool(*args)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_int8(int8):
        builder = _StructBuilder('hbxxxxxxxxxxxxxxxxxxxxx')
        __which__ = 2
        buf = builder.build(__which__, int8)
        return buf
    @classmethod
    def new_int8(cls, int8):
        buf = cls.__new_int8(int8)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_int16(int16):
        builder = _StructBuilder('hhxxxxxxxxxxxxxxxxxxxx')
        __which__ = 3
        buf = builder.build(__which__, int16)
        return buf
    @classmethod
    def new_int16(cls, int16):
        buf = cls.__new_int16(int16)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_int32(int32):
        builder = _StructBuilder('hxxixxxxxxxxxxxxxxxx')
        __which__ = 4
        buf = builder.build(__which__, int32)
        return buf
    @classmethod
    def new_int32(cls, int32):
        buf = cls.__new_int32(int32)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_int64(int64):
        builder = _StructBuilder('hxxxxxxqxxxxxxxx')
        __which__ = 5
        buf = builder.build(__which__, int64)
        return buf
    @classmethod
    def new_int64(cls, int64):
        buf = cls.__new_int64(int64)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_uint8(uint8):
        builder = _StructBuilder('hBxxxxxxxxxxxxxxxxxxxxx')
        __which__ = 6
        buf = builder.build(__which__, uint8)
        return buf
    @classmethod
    def new_uint8(cls, uint8):
        buf = cls.__new_uint8(uint8)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_uint16(uint16):
        builder = _StructBuilder('hHxxxxxxxxxxxxxxxxxxxx')
        __which__ = 7
        buf = builder.build(__which__, uint16)
        return buf
    @classmethod
    def new_uint16(cls, uint16):
        buf = cls.__new_uint16(uint16)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_uint32(uint32):
        builder = _StructBuilder('hxxIxxxxxxxxxxxxxxxx')
        __which__ = 8
        buf = builder.build(__which__, uint32)
        return buf
    @classmethod
    def new_uint32(cls, uint32):
        buf = cls.__new_uint32(uint32)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_uint64(uint64):
        builder = _StructBuilder('hxxxxxxQxxxxxxxx')
        __which__ = 9
        buf = builder.build(__which__, uint64)
        return buf
    @classmethod
    def new_uint64(cls, uint64):
        buf = cls.__new_uint64(uint64)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_float32(float32):
        builder = _StructBuilder('hxxfxxxxxxxxxxxxxxxx')
        __which__ = 10
        buf = builder.build(__which__, float32)
        return buf
    @classmethod
    def new_float32(cls, float32):
        buf = cls.__new_float32(float32)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_float64(float64):
        builder = _StructBuilder('hxxxxxxdxxxxxxxx')
        __which__ = 11
        buf = builder.build(__which__, float64)
        return buf
    @classmethod
    def new_float64(cls, float64):
        buf = cls.__new_float64(float64)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_text(text):
        builder = _StructBuilder('hxxxxxxxxxxxxxxq')
        __which__ = 12
        text = builder.alloc_string(16, text)
        buf = builder.build(__which__, text)
        return buf
    @classmethod
    def new_text(cls, text):
        buf = cls.__new_text(text)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_data(data):
        builder = _StructBuilder('hxxxxxxxxxxxxxxq')
        __which__ = 13
        raise NotImplementedError('Unsupported field type: <capnpy.schema_extended.Field__Slot object at 0x7f43ada39c90>')
        buf = builder.build(__which__, data)
        return buf
    @classmethod
    def new_data(cls, data):
        buf = cls.__new_data(data)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_list(list):
        builder = _StructBuilder('hxxxxxxxxxxxxxxq')
        __which__ = 14
        raise NotImplementedError('Unsupported field type: <capnpy.schema_extended.Field__Slot object at 0x7f43ada39d00>')
        buf = builder.build(__which__, list)
        return buf
    @classmethod
    def new_list(cls, list):
        buf = cls.__new_list(list)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_enum(enum):
        builder = _StructBuilder('hHxxxxxxxxxxxxxxxxxxxx')
        __which__ = 15
        buf = builder.build(__which__, enum)
        return buf
    @classmethod
    def new_enum(cls, enum):
        buf = cls.__new_enum(enum)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_struct(struct):
        builder = _StructBuilder('hxxxxxxxxxxxxxxq')
        __which__ = 16
        raise NotImplementedError('Unsupported field type: <capnpy.schema_extended.Field__Slot object at 0x7f43ada5da60>')
        buf = builder.build(__which__, struct)
        return buf
    @classmethod
    def new_struct(cls, struct):
        buf = cls.__new_struct(struct)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_interface():
        builder = _StructBuilder('hxxxxxxxxxxxxxxxxxxxxxx')
        __which__ = 17
        buf = builder.build(__which__)
        return buf
    @classmethod
    def new_interface(cls):
        buf = cls.__new_interface()
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_anyPointer(anyPointer):
        builder = _StructBuilder('hxxxxxxxxxxxxxxq')
        __which__ = 18
        raise NotImplementedError('Unsupported field type: <capnpy.schema_extended.Field__Slot object at 0x7f43ada5db40>')
        buf = builder.build(__which__, anyPointer)
        return buf
    @classmethod
    def new_anyPointer(cls, anyPointer):
        buf = cls.__new_anyPointer(anyPointer)
        return cls.from_buffer(buf, 0, 2, 1)
    
    def __init__(self, void=_undefined, bool=_undefined, int8=_undefined, int16=_undefined, int32=_undefined, int64=_undefined, uint8=_undefined, uint16=_undefined, uint32=_undefined, uint64=_undefined, float32=_undefined, float64=_undefined, text=_undefined, data=_undefined, list=_undefined, enum=_undefined, struct=_undefined, interface=_undefined, anyPointer=_undefined):
        if void is not _undefined:
            self._assert_undefined(bool, "bool", "void")
            self._assert_undefined(int8, "int8", "void")
            self._assert_undefined(int16, "int16", "void")
            self._assert_undefined(int32, "int32", "void")
            self._assert_undefined(int64, "int64", "void")
            self._assert_undefined(uint8, "uint8", "void")
            self._assert_undefined(uint16, "uint16", "void")
            self._assert_undefined(uint32, "uint32", "void")
            self._assert_undefined(uint64, "uint64", "void")
            self._assert_undefined(float32, "float32", "void")
            self._assert_undefined(float64, "float64", "void")
            self._assert_undefined(text, "text", "void")
            self._assert_undefined(data, "data", "void")
            self._assert_undefined(list, "list", "void")
            self._assert_undefined(enum, "enum", "void")
            self._assert_undefined(struct, "struct", "void")
            self._assert_undefined(interface, "interface", "void")
            self._assert_undefined(anyPointer, "anyPointer", "void")
            buf = self.__new_void(void=void)
            _Struct.__init__(self, buf, 0, 2, 1)
            return
        if bool is not _undefined:
            self._assert_undefined(void, "void", "bool")
            self._assert_undefined(int8, "int8", "bool")
            self._assert_undefined(int16, "int16", "bool")
            self._assert_undefined(int32, "int32", "bool")
            self._assert_undefined(int64, "int64", "bool")
            self._assert_undefined(uint8, "uint8", "bool")
            self._assert_undefined(uint16, "uint16", "bool")
            self._assert_undefined(uint32, "uint32", "bool")
            self._assert_undefined(uint64, "uint64", "bool")
            self._assert_undefined(float32, "float32", "bool")
            self._assert_undefined(float64, "float64", "bool")
            self._assert_undefined(text, "text", "bool")
            self._assert_undefined(data, "data", "bool")
            self._assert_undefined(list, "list", "bool")
            self._assert_undefined(enum, "enum", "bool")
            self._assert_undefined(struct, "struct", "bool")
            self._assert_undefined(interface, "interface", "bool")
            self._assert_undefined(anyPointer, "anyPointer", "bool")
            buf = self.__new_bool(bool=bool)
            _Struct.__init__(self, buf, 0, 2, 1)
            return
        if int8 is not _undefined:
            self._assert_undefined(void, "void", "int8")
            self._assert_undefined(bool, "bool", "int8")
            self._assert_undefined(int16, "int16", "int8")
            self._assert_undefined(int32, "int32", "int8")
            self._assert_undefined(int64, "int64", "int8")
            self._assert_undefined(uint8, "uint8", "int8")
            self._assert_undefined(uint16, "uint16", "int8")
            self._assert_undefined(uint32, "uint32", "int8")
            self._assert_undefined(uint64, "uint64", "int8")
            self._assert_undefined(float32, "float32", "int8")
            self._assert_undefined(float64, "float64", "int8")
            self._assert_undefined(text, "text", "int8")
            self._assert_undefined(data, "data", "int8")
            self._assert_undefined(list, "list", "int8")
            self._assert_undefined(enum, "enum", "int8")
            self._assert_undefined(struct, "struct", "int8")
            self._assert_undefined(interface, "interface", "int8")
            self._assert_undefined(anyPointer, "anyPointer", "int8")
            buf = self.__new_int8(int8=int8)
            _Struct.__init__(self, buf, 0, 2, 1)
            return
        if int16 is not _undefined:
            self._assert_undefined(void, "void", "int16")
            self._assert_undefined(bool, "bool", "int16")
            self._assert_undefined(int8, "int8", "int16")
            self._assert_undefined(int32, "int32", "int16")
            self._assert_undefined(int64, "int64", "int16")
            self._assert_undefined(uint8, "uint8", "int16")
            self._assert_undefined(uint16, "uint16", "int16")
            self._assert_undefined(uint32, "uint32", "int16")
            self._assert_undefined(uint64, "uint64", "int16")
            self._assert_undefined(float32, "float32", "int16")
            self._assert_undefined(float64, "float64", "int16")
            self._assert_undefined(text, "text", "int16")
            self._assert_undefined(data, "data", "int16")
            self._assert_undefined(list, "list", "int16")
            self._assert_undefined(enum, "enum", "int16")
            self._assert_undefined(struct, "struct", "int16")
            self._assert_undefined(interface, "interface", "int16")
            self._assert_undefined(anyPointer, "anyPointer", "int16")
            buf = self.__new_int16(int16=int16)
            _Struct.__init__(self, buf, 0, 2, 1)
            return
        if int32 is not _undefined:
            self._assert_undefined(void, "void", "int32")
            self._assert_undefined(bool, "bool", "int32")
            self._assert_undefined(int8, "int8", "int32")
            self._assert_undefined(int16, "int16", "int32")
            self._assert_undefined(int64, "int64", "int32")
            self._assert_undefined(uint8, "uint8", "int32")
            self._assert_undefined(uint16, "uint16", "int32")
            self._assert_undefined(uint32, "uint32", "int32")
            self._assert_undefined(uint64, "uint64", "int32")
            self._assert_undefined(float32, "float32", "int32")
            self._assert_undefined(float64, "float64", "int32")
            self._assert_undefined(text, "text", "int32")
            self._assert_undefined(data, "data", "int32")
            self._assert_undefined(list, "list", "int32")
            self._assert_undefined(enum, "enum", "int32")
            self._assert_undefined(struct, "struct", "int32")
            self._assert_undefined(interface, "interface", "int32")
            self._assert_undefined(anyPointer, "anyPointer", "int32")
            buf = self.__new_int32(int32=int32)
            _Struct.__init__(self, buf, 0, 2, 1)
            return
        if int64 is not _undefined:
            self._assert_undefined(void, "void", "int64")
            self._assert_undefined(bool, "bool", "int64")
            self._assert_undefined(int8, "int8", "int64")
            self._assert_undefined(int16, "int16", "int64")
            self._assert_undefined(int32, "int32", "int64")
            self._assert_undefined(uint8, "uint8", "int64")
            self._assert_undefined(uint16, "uint16", "int64")
            self._assert_undefined(uint32, "uint32", "int64")
            self._assert_undefined(uint64, "uint64", "int64")
            self._assert_undefined(float32, "float32", "int64")
            self._assert_undefined(float64, "float64", "int64")
            self._assert_undefined(text, "text", "int64")
            self._assert_undefined(data, "data", "int64")
            self._assert_undefined(list, "list", "int64")
            self._assert_undefined(enum, "enum", "int64")
            self._assert_undefined(struct, "struct", "int64")
            self._assert_undefined(interface, "interface", "int64")
            self._assert_undefined(anyPointer, "anyPointer", "int64")
            buf = self.__new_int64(int64=int64)
            _Struct.__init__(self, buf, 0, 2, 1)
            return
        if uint8 is not _undefined:
            self._assert_undefined(void, "void", "uint8")
            self._assert_undefined(bool, "bool", "uint8")
            self._assert_undefined(int8, "int8", "uint8")
            self._assert_undefined(int16, "int16", "uint8")
            self._assert_undefined(int32, "int32", "uint8")
            self._assert_undefined(int64, "int64", "uint8")
            self._assert_undefined(uint16, "uint16", "uint8")
            self._assert_undefined(uint32, "uint32", "uint8")
            self._assert_undefined(uint64, "uint64", "uint8")
            self._assert_undefined(float32, "float32", "uint8")
            self._assert_undefined(float64, "float64", "uint8")
            self._assert_undefined(text, "text", "uint8")
            self._assert_undefined(data, "data", "uint8")
            self._assert_undefined(list, "list", "uint8")
            self._assert_undefined(enum, "enum", "uint8")
            self._assert_undefined(struct, "struct", "uint8")
            self._assert_undefined(interface, "interface", "uint8")
            self._assert_undefined(anyPointer, "anyPointer", "uint8")
            buf = self.__new_uint8(uint8=uint8)
            _Struct.__init__(self, buf, 0, 2, 1)
            return
        if uint16 is not _undefined:
            self._assert_undefined(void, "void", "uint16")
            self._assert_undefined(bool, "bool", "uint16")
            self._assert_undefined(int8, "int8", "uint16")
            self._assert_undefined(int16, "int16", "uint16")
            self._assert_undefined(int32, "int32", "uint16")
            self._assert_undefined(int64, "int64", "uint16")
            self._assert_undefined(uint8, "uint8", "uint16")
            self._assert_undefined(uint32, "uint32", "uint16")
            self._assert_undefined(uint64, "uint64", "uint16")
            self._assert_undefined(float32, "float32", "uint16")
            self._assert_undefined(float64, "float64", "uint16")
            self._assert_undefined(text, "text", "uint16")
            self._assert_undefined(data, "data", "uint16")
            self._assert_undefined(list, "list", "uint16")
            self._assert_undefined(enum, "enum", "uint16")
            self._assert_undefined(struct, "struct", "uint16")
            self._assert_undefined(interface, "interface", "uint16")
            self._assert_undefined(anyPointer, "anyPointer", "uint16")
            buf = self.__new_uint16(uint16=uint16)
            _Struct.__init__(self, buf, 0, 2, 1)
            return
        if uint32 is not _undefined:
            self._assert_undefined(void, "void", "uint32")
            self._assert_undefined(bool, "bool", "uint32")
            self._assert_undefined(int8, "int8", "uint32")
            self._assert_undefined(int16, "int16", "uint32")
            self._assert_undefined(int32, "int32", "uint32")
            self._assert_undefined(int64, "int64", "uint32")
            self._assert_undefined(uint8, "uint8", "uint32")
            self._assert_undefined(uint16, "uint16", "uint32")
            self._assert_undefined(uint64, "uint64", "uint32")
            self._assert_undefined(float32, "float32", "uint32")
            self._assert_undefined(float64, "float64", "uint32")
            self._assert_undefined(text, "text", "uint32")
            self._assert_undefined(data, "data", "uint32")
            self._assert_undefined(list, "list", "uint32")
            self._assert_undefined(enum, "enum", "uint32")
            self._assert_undefined(struct, "struct", "uint32")
            self._assert_undefined(interface, "interface", "uint32")
            self._assert_undefined(anyPointer, "anyPointer", "uint32")
            buf = self.__new_uint32(uint32=uint32)
            _Struct.__init__(self, buf, 0, 2, 1)
            return
        if uint64 is not _undefined:
            self._assert_undefined(void, "void", "uint64")
            self._assert_undefined(bool, "bool", "uint64")
            self._assert_undefined(int8, "int8", "uint64")
            self._assert_undefined(int16, "int16", "uint64")
            self._assert_undefined(int32, "int32", "uint64")
            self._assert_undefined(int64, "int64", "uint64")
            self._assert_undefined(uint8, "uint8", "uint64")
            self._assert_undefined(uint16, "uint16", "uint64")
            self._assert_undefined(uint32, "uint32", "uint64")
            self._assert_undefined(float32, "float32", "uint64")
            self._assert_undefined(float64, "float64", "uint64")
            self._assert_undefined(text, "text", "uint64")
            self._assert_undefined(data, "data", "uint64")
            self._assert_undefined(list, "list", "uint64")
            self._assert_undefined(enum, "enum", "uint64")
            self._assert_undefined(struct, "struct", "uint64")
            self._assert_undefined(interface, "interface", "uint64")
            self._assert_undefined(anyPointer, "anyPointer", "uint64")
            buf = self.__new_uint64(uint64=uint64)
            _Struct.__init__(self, buf, 0, 2, 1)
            return
        if float32 is not _undefined:
            self._assert_undefined(void, "void", "float32")
            self._assert_undefined(bool, "bool", "float32")
            self._assert_undefined(int8, "int8", "float32")
            self._assert_undefined(int16, "int16", "float32")
            self._assert_undefined(int32, "int32", "float32")
            self._assert_undefined(int64, "int64", "float32")
            self._assert_undefined(uint8, "uint8", "float32")
            self._assert_undefined(uint16, "uint16", "float32")
            self._assert_undefined(uint32, "uint32", "float32")
            self._assert_undefined(uint64, "uint64", "float32")
            self._assert_undefined(float64, "float64", "float32")
            self._assert_undefined(text, "text", "float32")
            self._assert_undefined(data, "data", "float32")
            self._assert_undefined(list, "list", "float32")
            self._assert_undefined(enum, "enum", "float32")
            self._assert_undefined(struct, "struct", "float32")
            self._assert_undefined(interface, "interface", "float32")
            self._assert_undefined(anyPointer, "anyPointer", "float32")
            buf = self.__new_float32(float32=float32)
            _Struct.__init__(self, buf, 0, 2, 1)
            return
        if float64 is not _undefined:
            self._assert_undefined(void, "void", "float64")
            self._assert_undefined(bool, "bool", "float64")
            self._assert_undefined(int8, "int8", "float64")
            self._assert_undefined(int16, "int16", "float64")
            self._assert_undefined(int32, "int32", "float64")
            self._assert_undefined(int64, "int64", "float64")
            self._assert_undefined(uint8, "uint8", "float64")
            self._assert_undefined(uint16, "uint16", "float64")
            self._assert_undefined(uint32, "uint32", "float64")
            self._assert_undefined(uint64, "uint64", "float64")
            self._assert_undefined(float32, "float32", "float64")
            self._assert_undefined(text, "text", "float64")
            self._assert_undefined(data, "data", "float64")
            self._assert_undefined(list, "list", "float64")
            self._assert_undefined(enum, "enum", "float64")
            self._assert_undefined(struct, "struct", "float64")
            self._assert_undefined(interface, "interface", "float64")
            self._assert_undefined(anyPointer, "anyPointer", "float64")
            buf = self.__new_float64(float64=float64)
            _Struct.__init__(self, buf, 0, 2, 1)
            return
        if text is not _undefined:
            self._assert_undefined(void, "void", "text")
            self._assert_undefined(bool, "bool", "text")
            self._assert_undefined(int8, "int8", "text")
            self._assert_undefined(int16, "int16", "text")
            self._assert_undefined(int32, "int32", "text")
            self._assert_undefined(int64, "int64", "text")
            self._assert_undefined(uint8, "uint8", "text")
            self._assert_undefined(uint16, "uint16", "text")
            self._assert_undefined(uint32, "uint32", "text")
            self._assert_undefined(uint64, "uint64", "text")
            self._assert_undefined(float32, "float32", "text")
            self._assert_undefined(float64, "float64", "text")
            self._assert_undefined(data, "data", "text")
            self._assert_undefined(list, "list", "text")
            self._assert_undefined(enum, "enum", "text")
            self._assert_undefined(struct, "struct", "text")
            self._assert_undefined(interface, "interface", "text")
            self._assert_undefined(anyPointer, "anyPointer", "text")
            buf = self.__new_text(text=text)
            _Struct.__init__(self, buf, 0, 2, 1)
            return
        if data is not _undefined:
            self._assert_undefined(void, "void", "data")
            self._assert_undefined(bool, "bool", "data")
            self._assert_undefined(int8, "int8", "data")
            self._assert_undefined(int16, "int16", "data")
            self._assert_undefined(int32, "int32", "data")
            self._assert_undefined(int64, "int64", "data")
            self._assert_undefined(uint8, "uint8", "data")
            self._assert_undefined(uint16, "uint16", "data")
            self._assert_undefined(uint32, "uint32", "data")
            self._assert_undefined(uint64, "uint64", "data")
            self._assert_undefined(float32, "float32", "data")
            self._assert_undefined(float64, "float64", "data")
            self._assert_undefined(text, "text", "data")
            self._assert_undefined(list, "list", "data")
            self._assert_undefined(enum, "enum", "data")
            self._assert_undefined(struct, "struct", "data")
            self._assert_undefined(interface, "interface", "data")
            self._assert_undefined(anyPointer, "anyPointer", "data")
            buf = self.__new_data(data=data)
            _Struct.__init__(self, buf, 0, 2, 1)
            return
        if list is not _undefined:
            self._assert_undefined(void, "void", "list")
            self._assert_undefined(bool, "bool", "list")
            self._assert_undefined(int8, "int8", "list")
            self._assert_undefined(int16, "int16", "list")
            self._assert_undefined(int32, "int32", "list")
            self._assert_undefined(int64, "int64", "list")
            self._assert_undefined(uint8, "uint8", "list")
            self._assert_undefined(uint16, "uint16", "list")
            self._assert_undefined(uint32, "uint32", "list")
            self._assert_undefined(uint64, "uint64", "list")
            self._assert_undefined(float32, "float32", "list")
            self._assert_undefined(float64, "float64", "list")
            self._assert_undefined(text, "text", "list")
            self._assert_undefined(data, "data", "list")
            self._assert_undefined(enum, "enum", "list")
            self._assert_undefined(struct, "struct", "list")
            self._assert_undefined(interface, "interface", "list")
            self._assert_undefined(anyPointer, "anyPointer", "list")
            buf = self.__new_list(list=list)
            _Struct.__init__(self, buf, 0, 2, 1)
            return
        if enum is not _undefined:
            self._assert_undefined(void, "void", "enum")
            self._assert_undefined(bool, "bool", "enum")
            self._assert_undefined(int8, "int8", "enum")
            self._assert_undefined(int16, "int16", "enum")
            self._assert_undefined(int32, "int32", "enum")
            self._assert_undefined(int64, "int64", "enum")
            self._assert_undefined(uint8, "uint8", "enum")
            self._assert_undefined(uint16, "uint16", "enum")
            self._assert_undefined(uint32, "uint32", "enum")
            self._assert_undefined(uint64, "uint64", "enum")
            self._assert_undefined(float32, "float32", "enum")
            self._assert_undefined(float64, "float64", "enum")
            self._assert_undefined(text, "text", "enum")
            self._assert_undefined(data, "data", "enum")
            self._assert_undefined(list, "list", "enum")
            self._assert_undefined(struct, "struct", "enum")
            self._assert_undefined(interface, "interface", "enum")
            self._assert_undefined(anyPointer, "anyPointer", "enum")
            buf = self.__new_enum(enum=enum)
            _Struct.__init__(self, buf, 0, 2, 1)
            return
        if struct is not _undefined:
            self._assert_undefined(void, "void", "struct")
            self._assert_undefined(bool, "bool", "struct")
            self._assert_undefined(int8, "int8", "struct")
            self._assert_undefined(int16, "int16", "struct")
            self._assert_undefined(int32, "int32", "struct")
            self._assert_undefined(int64, "int64", "struct")
            self._assert_undefined(uint8, "uint8", "struct")
            self._assert_undefined(uint16, "uint16", "struct")
            self._assert_undefined(uint32, "uint32", "struct")
            self._assert_undefined(uint64, "uint64", "struct")
            self._assert_undefined(float32, "float32", "struct")
            self._assert_undefined(float64, "float64", "struct")
            self._assert_undefined(text, "text", "struct")
            self._assert_undefined(data, "data", "struct")
            self._assert_undefined(list, "list", "struct")
            self._assert_undefined(enum, "enum", "struct")
            self._assert_undefined(interface, "interface", "struct")
            self._assert_undefined(anyPointer, "anyPointer", "struct")
            buf = self.__new_struct(struct=struct)
            _Struct.__init__(self, buf, 0, 2, 1)
            return
        if interface is not _undefined:
            self._assert_undefined(void, "void", "interface")
            self._assert_undefined(bool, "bool", "interface")
            self._assert_undefined(int8, "int8", "interface")
            self._assert_undefined(int16, "int16", "interface")
            self._assert_undefined(int32, "int32", "interface")
            self._assert_undefined(int64, "int64", "interface")
            self._assert_undefined(uint8, "uint8", "interface")
            self._assert_undefined(uint16, "uint16", "interface")
            self._assert_undefined(uint32, "uint32", "interface")
            self._assert_undefined(uint64, "uint64", "interface")
            self._assert_undefined(float32, "float32", "interface")
            self._assert_undefined(float64, "float64", "interface")
            self._assert_undefined(text, "text", "interface")
            self._assert_undefined(data, "data", "interface")
            self._assert_undefined(list, "list", "interface")
            self._assert_undefined(enum, "enum", "interface")
            self._assert_undefined(struct, "struct", "interface")
            self._assert_undefined(anyPointer, "anyPointer", "interface")
            buf = self.__new_interface(interface=interface)
            _Struct.__init__(self, buf, 0, 2, 1)
            return
        if anyPointer is not _undefined:
            self._assert_undefined(void, "void", "anyPointer")
            self._assert_undefined(bool, "bool", "anyPointer")
            self._assert_undefined(int8, "int8", "anyPointer")
            self._assert_undefined(int16, "int16", "anyPointer")
            self._assert_undefined(int32, "int32", "anyPointer")
            self._assert_undefined(int64, "int64", "anyPointer")
            self._assert_undefined(uint8, "uint8", "anyPointer")
            self._assert_undefined(uint16, "uint16", "anyPointer")
            self._assert_undefined(uint32, "uint32", "anyPointer")
            self._assert_undefined(uint64, "uint64", "anyPointer")
            self._assert_undefined(float32, "float32", "anyPointer")
            self._assert_undefined(float64, "float64", "anyPointer")
            self._assert_undefined(text, "text", "anyPointer")
            self._assert_undefined(data, "data", "anyPointer")
            self._assert_undefined(list, "list", "anyPointer")
            self._assert_undefined(enum, "enum", "anyPointer")
            self._assert_undefined(struct, "struct", "anyPointer")
            self._assert_undefined(interface, "interface", "anyPointer")
            buf = self.__new_anyPointer(anyPointer=anyPointer)
            _Struct.__init__(self, buf, 0, 2, 1)
            return
        raise TypeError("one of the following args is required: void, bool, int8, int16, int32, int64, uint8, uint16, uint32, uint64, float32, float64, text, data, list, enum, struct, interface, anyPointer")
    
    def shortrepr(self):
        parts = [
            "(",
            "void = ", str(self.void), ", ",
            "bool = ", str(self.bool), ", ",
            "int8 = ", str(self.int8), ", ",
            "int16 = ", str(self.int16), ", ",
            "int32 = ", str(self.int32), ", ",
            "int64 = ", str(self.int64), ", ",
            "uint8 = ", str(self.uint8), ", ",
            "uint16 = ", str(self.uint16), ", ",
            "uint32 = ", str(self.uint32), ", ",
            "uint64 = ", str(self.uint64), ", ",
            "float32 = ", str(self.float32), ", ",
            "float64 = ", str(self.float64), ", ",
            "text = ", str(self.text), ", ",
            "data = ", str(self.data), ", ",
            "list = ", str(self.list), ", ",
            "enum = ", str(self.enum), ", ",
            "struct = ", str(self.struct), ", ",
            "interface = ", str(self.interface), ", ",
            "anyPointer = ", str(self.anyPointer), 
            ")"
            ]
        return "".join(parts)


@Brand_Binding.__extend__
class Brand_Binding(_Struct):
    __static_data_size__ = 1
    __static_ptrs_size__ = 1
    
    
    __tag_offset__ = 0
    __tag__ = _enum('Binding.__tag__', ('unbound', 'type'))
    
    @property
    def unbound(self):
        self._ensure_union(0)
        return None
    
    @property
    def type(self):
        self._ensure_union(1)
        return self._read_struct(0, Type)
    
    def has_type(self):
        offset, ptr = self._read_ptr(0)
        return ptr != 0
    
    @staticmethod
    def __new_unbound():
        builder = _StructBuilder('hxxxxxxxxxxxxxx')
        __which__ = 0
        buf = builder.build(__which__)
        return buf
    @classmethod
    def new_unbound(cls):
        buf = cls.__new_unbound()
        return cls.from_buffer(buf, 0, 1, 1)
    
    @staticmethod
    def __new_type(type):
        builder = _StructBuilder('hxxxxxxq')
        __which__ = 1
        type = builder.alloc_struct(8, Type, type)
        buf = builder.build(__which__, type)
        return buf
    @classmethod
    def new_type(cls, type):
        buf = cls.__new_type(type)
        return cls.from_buffer(buf, 0, 1, 1)
    
    def __init__(self, unbound=_undefined, type=_undefined):
        if unbound is not _undefined:
            self._assert_undefined(type, "type", "unbound")
            buf = self.__new_unbound(unbound=unbound)
            _Struct.__init__(self, buf, 0, 1, 1)
            return
        if type is not _undefined:
            self._assert_undefined(unbound, "unbound", "type")
            buf = self.__new_type(type=type)
            _Struct.__init__(self, buf, 0, 1, 1)
            return
        raise TypeError("one of the following args is required: unbound, type")
    
    def shortrepr(self):
        parts = [
            "(",
            "unbound = ", str(self.unbound), ", ",
            "type = ", str(self.type), 
            ")"
            ]
        return "".join(parts)


@Brand_Scope.__extend__
class Brand_Scope(_Struct):
    __static_data_size__ = 2
    __static_ptrs_size__ = 1
    
    
    __tag_offset__ = 8
    __tag__ = _enum('Scope.__tag__', ('bind', 'inherit'))
    
    @property
    def scopeId(self):
        # no union check
        value = self._read_data(0, ord('Q'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @property
    def bind(self):
        self._ensure_union(0)
        return self._read_list(0, _StructList, Brand.Binding)
    
    def has_bind(self):
        offset, ptr = self._read_ptr(0)
        return ptr != 0
    
    @property
    def inherit(self):
        self._ensure_union(1)
        return None
    
    @staticmethod
    def __new_bind(bind, scopeId):
        builder = _StructBuilder('Qhxxxxxxq')
        __which__ = 0
        bind = builder.alloc_list(16, _StructList, Brand.Binding, bind)
        buf = builder.build(scopeId, __which__, bind)
        return buf
    @classmethod
    def new_bind(cls, bind, scopeId):
        buf = cls.__new_bind(bind, scopeId)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_inherit(scopeId):
        builder = _StructBuilder('Qhxxxxxxxxxxxxxx')
        __which__ = 1
        buf = builder.build(scopeId, __which__)
        return buf
    @classmethod
    def new_inherit(cls, scopeId):
        buf = cls.__new_inherit(scopeId)
        return cls.from_buffer(buf, 0, 2, 1)
    
    def __init__(self, scopeId, bind=_undefined, inherit=_undefined):
        if bind is not _undefined:
            self._assert_undefined(inherit, "inherit", "bind")
            buf = self.__new_bind(scopeId=scopeId, bind=bind)
            _Struct.__init__(self, buf, 0, 2, 1)
            return
        if inherit is not _undefined:
            self._assert_undefined(bind, "bind", "inherit")
            buf = self.__new_inherit(scopeId=scopeId, inherit=inherit)
            _Struct.__init__(self, buf, 0, 2, 1)
            return
        raise TypeError("one of the following args is required: bind, inherit")
    
    def shortrepr(self):
        parts = [
            "(",
            "scopeId = ", str(self.scopeId), ", ",
            "bind = ", str(self.bind), ", ",
            "inherit = ", str(self.inherit), 
            ")"
            ]
        return "".join(parts)


@Brand.__extend__
class Brand(_Struct):
    __static_data_size__ = 0
    __static_ptrs_size__ = 1
    
    Binding = Brand_Binding
    Scope = Brand_Scope
    
    @property
    def scopes(self):
        # no union check
        return self._read_list(0, _StructList, Brand.Scope)
    
    def has_scopes(self):
        offset, ptr = self._read_ptr(0)
        return ptr != 0
    
    @staticmethod
    def __new(scopes):
        builder = _StructBuilder('q')
        scopes = builder.alloc_list(0, _StructList, Brand.Scope, scopes)
        buf = builder.build(scopes)
        return buf
    
    def __init__(self, scopes):
        buf = self.__new(scopes)
        _Struct.__init__(self, buf, 0, 0, 1)
    
    def shortrepr(self):
        parts = [
            "(",
            "scopes = ", str(self.scopes), 
            ")"
            ]
        return "".join(parts)


@Annotation.__extend__
class Annotation(_Struct):
    __static_data_size__ = 1
    __static_ptrs_size__ = 2
    
    
    @property
    def id(self):
        # no union check
        value = self._read_data(0, ord('Q'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @property
    def value(self):
        # no union check
        return self._read_struct(0, Value)
    
    def has_value(self):
        offset, ptr = self._read_ptr(0)
        return ptr != 0
    
    @property
    def brand(self):
        # no union check
        return self._read_struct(8, Brand)
    
    def has_brand(self):
        offset, ptr = self._read_ptr(8)
        return ptr != 0
    
    @staticmethod
    def __new(id, value, brand):
        builder = _StructBuilder('Qqq')
        value = builder.alloc_struct(8, Value, value)
        brand = builder.alloc_struct(16, Brand, brand)
        buf = builder.build(id, value, brand)
        return buf
    
    def __init__(self, id, value, brand):
        buf = self.__new(id, value, brand)
        _Struct.__init__(self, buf, 0, 1, 2)
    
    def shortrepr(self):
        parts = [
            "(",
            "id = ", str(self.id), ", ",
            "value = ", str(self.value), ", ",
            "brand = ", str(self.brand), 
            ")"
            ]
        return "".join(parts)


@Node_interface.__extend__
class Node_interface(_Struct):
    __static_data_size__ = 5
    __static_ptrs_size__ = 6
    
    
    @property
    def methods(self):
        # no union check
        return self._read_list(24, _StructList, Method)
    
    def has_methods(self):
        offset, ptr = self._read_ptr(24)
        return ptr != 0
    
    @property
    def superclasses(self):
        # no union check
        return self._read_list(32, _StructList, Superclass)
    
    def has_superclasses(self):
        offset, ptr = self._read_ptr(32)
        return ptr != 0
    
    @staticmethod
    def __new(methods, superclasses):
        builder = _StructBuilder('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxqqxxxxxxxx')
        methods = builder.alloc_list(64, _StructList, Method, methods)
        superclasses = builder.alloc_list(72, _StructList, Superclass, superclasses)
        buf = builder.build(methods, superclasses)
        return buf
    
    def __init__(self, methods, superclasses):
        buf = self.__new(methods, superclasses)
        _Struct.__init__(self, buf, 0, 5, 6)
    
    def shortrepr(self):
        parts = [
            "(",
            "methods = ", str(self.methods), ", ",
            "superclasses = ", str(self.superclasses), 
            ")"
            ]
        return "".join(parts)


@Node_const.__extend__
class Node_const(_Struct):
    __static_data_size__ = 5
    __static_ptrs_size__ = 6
    
    
    @property
    def type(self):
        # no union check
        return self._read_struct(24, Type)
    
    def has_type(self):
        offset, ptr = self._read_ptr(24)
        return ptr != 0
    
    @property
    def value(self):
        # no union check
        return self._read_struct(32, Value)
    
    def has_value(self):
        offset, ptr = self._read_ptr(32)
        return ptr != 0
    
    @staticmethod
    def __new(type, value):
        builder = _StructBuilder('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxqqxxxxxxxx')
        type = builder.alloc_struct(64, Type, type)
        value = builder.alloc_struct(72, Value, value)
        buf = builder.build(type, value)
        return buf
    
    def __init__(self, type, value):
        buf = self.__new(type, value)
        _Struct.__init__(self, buf, 0, 5, 6)
    
    def shortrepr(self):
        parts = [
            "(",
            "type = ", str(self.type), ", ",
            "value = ", str(self.value), 
            ")"
            ]
        return "".join(parts)


@Node_struct.__extend__
class Node_struct(_Struct):
    __static_data_size__ = 5
    __static_ptrs_size__ = 6
    
    
    @property
    def dataWordCount(self):
        # no union check
        value = self._read_data(14, ord('H'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @property
    def pointerCount(self):
        # no union check
        value = self._read_data(24, ord('H'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @property
    def preferredListEncoding(self):
        # no union check
        return self._read_enum(26, ElementSize)
    
    @property
    def isGroup(self):
        # no union check
        value = self._read_bit(28, 1)
        if False != 0:
            value = value ^ False
        return value
    
    @property
    def discriminantCount(self):
        # no union check
        value = self._read_data(30, ord('H'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @property
    def discriminantOffset(self):
        # no union check
        value = self._read_data(32, ord('I'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @property
    def fields(self):
        # no union check
        return self._read_list(24, _StructList, Field)
    
    def has_fields(self):
        offset, ptr = self._read_ptr(24)
        return ptr != 0
    
    @staticmethod
    def __new(*args, **kwargs):
        raise NotImplementedError('Unsupported field type: <capnpy.schema_extended.Field__Slot object at 0x7f43ada39b40>')
    
    def __init__(self, *args):
        buf = self.__new(*args)
        _Struct.__init__(self, buf, 0, 5, 6)
    
    def shortrepr(self):
        parts = [
            "(",
            "dataWordCount = ", str(self.dataWordCount), ", ",
            "pointerCount = ", str(self.pointerCount), ", ",
            "preferredListEncoding = ", str(self.preferredListEncoding), ", ",
            "isGroup = ", str(self.isGroup), ", ",
            "discriminantCount = ", str(self.discriminantCount), ", ",
            "discriminantOffset = ", str(self.discriminantOffset), ", ",
            "fields = ", str(self.fields), 
            ")"
            ]
        return "".join(parts)


@Node_annotation.__extend__
class Node_annotation(_Struct):
    __static_data_size__ = 5
    __static_ptrs_size__ = 6
    
    
    @property
    def type(self):
        # no union check
        return self._read_struct(24, Type)
    
    def has_type(self):
        offset, ptr = self._read_ptr(24)
        return ptr != 0
    
    @property
    def targetsFile(self):
        # no union check
        value = self._read_bit(14, 1)
        if False != 0:
            value = value ^ False
        return value
    
    @property
    def targetsConst(self):
        # no union check
        value = self._read_bit(14, 2)
        if False != 0:
            value = value ^ False
        return value
    
    @property
    def targetsEnum(self):
        # no union check
        value = self._read_bit(14, 4)
        if False != 0:
            value = value ^ False
        return value
    
    @property
    def targetsEnumerant(self):
        # no union check
        value = self._read_bit(14, 8)
        if False != 0:
            value = value ^ False
        return value
    
    @property
    def targetsStruct(self):
        # no union check
        value = self._read_bit(14, 16)
        if False != 0:
            value = value ^ False
        return value
    
    @property
    def targetsField(self):
        # no union check
        value = self._read_bit(14, 32)
        if False != 0:
            value = value ^ False
        return value
    
    @property
    def targetsUnion(self):
        # no union check
        value = self._read_bit(14, 64)
        if False != 0:
            value = value ^ False
        return value
    
    @property
    def targetsGroup(self):
        # no union check
        value = self._read_bit(14, 128)
        if False != 0:
            value = value ^ False
        return value
    
    @property
    def targetsInterface(self):
        # no union check
        value = self._read_bit(15, 1)
        if False != 0:
            value = value ^ False
        return value
    
    @property
    def targetsMethod(self):
        # no union check
        value = self._read_bit(15, 2)
        if False != 0:
            value = value ^ False
        return value
    
    @property
    def targetsParam(self):
        # no union check
        value = self._read_bit(15, 4)
        if False != 0:
            value = value ^ False
        return value
    
    @property
    def targetsAnnotation(self):
        # no union check
        value = self._read_bit(15, 8)
        if False != 0:
            value = value ^ False
        return value
    
    @staticmethod
    def __new(*args, **kwargs):
        raise NotImplementedError('Unsupported field type: <capnpy.schema_extended.Field__Slot object at 0x7f43ada39c90>')
    
    def __init__(self, *args):
        buf = self.__new(*args)
        _Struct.__init__(self, buf, 0, 5, 6)
    
    def shortrepr(self):
        parts = [
            "(",
            "type = ", str(self.type), ", ",
            "targetsFile = ", str(self.targetsFile), ", ",
            "targetsConst = ", str(self.targetsConst), ", ",
            "targetsEnum = ", str(self.targetsEnum), ", ",
            "targetsEnumerant = ", str(self.targetsEnumerant), ", ",
            "targetsStruct = ", str(self.targetsStruct), ", ",
            "targetsField = ", str(self.targetsField), ", ",
            "targetsUnion = ", str(self.targetsUnion), ", ",
            "targetsGroup = ", str(self.targetsGroup), ", ",
            "targetsInterface = ", str(self.targetsInterface), ", ",
            "targetsMethod = ", str(self.targetsMethod), ", ",
            "targetsParam = ", str(self.targetsParam), ", ",
            "targetsAnnotation = ", str(self.targetsAnnotation), 
            ")"
            ]
        return "".join(parts)


@Node_enum.__extend__
class Node_enum(_Struct):
    __static_data_size__ = 5
    __static_ptrs_size__ = 6
    
    
    @property
    def enumerants(self):
        # no union check
        return self._read_list(24, _StructList, Enumerant)
    
    def has_enumerants(self):
        offset, ptr = self._read_ptr(24)
        return ptr != 0
    
    @staticmethod
    def __new(enumerants):
        builder = _StructBuilder('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxqxxxxxxxxxxxxxxxx')
        enumerants = builder.alloc_list(64, _StructList, Enumerant, enumerants)
        buf = builder.build(enumerants)
        return buf
    
    def __init__(self, enumerants):
        buf = self.__new(enumerants)
        _Struct.__init__(self, buf, 0, 5, 6)
    
    def shortrepr(self):
        parts = [
            "(",
            "enumerants = ", str(self.enumerants), 
            ")"
            ]
        return "".join(parts)


@Node_NestedNode.__extend__
class Node_NestedNode(_Struct):
    __static_data_size__ = 1
    __static_ptrs_size__ = 1
    
    
    @property
    def name(self):
        # no union check
        return self._read_str_text(0)
    
    def has_name(self):
        offset, ptr = self._read_ptr(0)
        return ptr != 0
    
    @property
    def id(self):
        # no union check
        value = self._read_data(0, ord('Q'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @staticmethod
    def __new(name, id):
        builder = _StructBuilder('Qq')
        name = builder.alloc_string(8, name)
        buf = builder.build(id, name)
        return buf
    
    def __init__(self, name, id):
        buf = self.__new(name, id)
        _Struct.__init__(self, buf, 0, 1, 1)
    
    def shortrepr(self):
        parts = [
            "(",
            "name = ", str(self.name), ", ",
            "id = ", str(self.id), 
            ")"
            ]
        return "".join(parts)


@Node_Parameter.__extend__
class Node_Parameter(_Struct):
    __static_data_size__ = 0
    __static_ptrs_size__ = 1
    
    
    @property
    def name(self):
        # no union check
        return self._read_str_text(0)
    
    def has_name(self):
        offset, ptr = self._read_ptr(0)
        return ptr != 0
    
    @staticmethod
    def __new(name):
        builder = _StructBuilder('q')
        name = builder.alloc_string(0, name)
        buf = builder.build(name)
        return buf
    
    def __init__(self, name):
        buf = self.__new(name)
        _Struct.__init__(self, buf, 0, 0, 1)
    
    def shortrepr(self):
        parts = [
            "(",
            "name = ", str(self.name), 
            ")"
            ]
        return "".join(parts)


@Node.__extend__
class Node(_Struct):
    __static_data_size__ = 5
    __static_ptrs_size__ = 6
    
    NestedNode = Node_NestedNode
    Parameter = Node_Parameter
    
    __tag_offset__ = 12
    __tag__ = _enum('Node.__tag__', ('file', 'struct', 'enum', 'interface', 'const', 'annotation'))
    
    @property
    def id(self):
        # no union check
        value = self._read_data(0, ord('Q'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @property
    def displayName(self):
        # no union check
        return self._read_str_text(0)
    
    def has_displayName(self):
        offset, ptr = self._read_ptr(0)
        return ptr != 0
    
    @property
    def displayNamePrefixLength(self):
        # no union check
        value = self._read_data(8, ord('I'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @property
    def scopeId(self):
        # no union check
        value = self._read_data(16, ord('Q'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @property
    def nestedNodes(self):
        # no union check
        return self._read_list(8, _StructList, Node.NestedNode)
    
    def has_nestedNodes(self):
        offset, ptr = self._read_ptr(8)
        return ptr != 0
    
    @property
    def annotations(self):
        # no union check
        return self._read_list(16, _StructList, Annotation)
    
    def has_annotations(self):
        offset, ptr = self._read_ptr(16)
        return ptr != 0
    
    @property
    def file(self):
        self._ensure_union(0)
        return None
    
    @property
    def struct(self):
        self._ensure_union(1)
        return self._read_group(Node_struct)
    
    @property
    def enum(self):
        self._ensure_union(2)
        return self._read_group(Node_enum)
    
    @property
    def interface(self):
        self._ensure_union(3)
        return self._read_group(Node_interface)
    
    @property
    def const(self):
        self._ensure_union(4)
        return self._read_group(Node_const)
    
    @property
    def annotation(self):
        self._ensure_union(5)
        return self._read_group(Node_annotation)
    
    @property
    def parameters(self):
        # no union check
        return self._read_list(40, _StructList, Node.Parameter)
    
    def has_parameters(self):
        offset, ptr = self._read_ptr(40)
        return ptr != 0
    
    @property
    def isGeneric(self):
        # no union check
        value = self._read_bit(36, 1)
        if False != 0:
            value = value ^ False
        return value
    
    @staticmethod
    def __new_file(*args, **kwargs):
        raise NotImplementedError('Unsupported field type: <capnpy.schema_extended.Field__Slot object at 0x7f43ada77980>')
    @classmethod
    def new_file(cls, *args):
        buf = cls.__new_file(*args)
        return cls.from_buffer(buf, 0, 5, 6)
    
    @staticmethod
    def __new_struct(*args, **kwargs):
        raise NotImplementedError('Group fields not supported yet')
    @classmethod
    def new_struct(cls, *args):
        buf = cls.__new_struct(*args)
        return cls.from_buffer(buf, 0, 5, 6)
    
    @staticmethod
    def __new_enum(*args, **kwargs):
        raise NotImplementedError('Group fields not supported yet')
    @classmethod
    def new_enum(cls, *args):
        buf = cls.__new_enum(*args)
        return cls.from_buffer(buf, 0, 5, 6)
    
    @staticmethod
    def __new_interface(*args, **kwargs):
        raise NotImplementedError('Group fields not supported yet')
    @classmethod
    def new_interface(cls, *args):
        buf = cls.__new_interface(*args)
        return cls.from_buffer(buf, 0, 5, 6)
    
    @staticmethod
    def __new_const(*args, **kwargs):
        raise NotImplementedError('Group fields not supported yet')
    @classmethod
    def new_const(cls, *args):
        buf = cls.__new_const(*args)
        return cls.from_buffer(buf, 0, 5, 6)
    
    @staticmethod
    def __new_annotation(*args, **kwargs):
        raise NotImplementedError('Group fields not supported yet')
    @classmethod
    def new_annotation(cls, *args):
        buf = cls.__new_annotation(*args)
        return cls.from_buffer(buf, 0, 5, 6)
    
    def __init__(self, id, displayName, displayNamePrefixLength, scopeId, nestedNodes, annotations, parameters, isGeneric, file=_undefined, struct=_undefined, enum=_undefined, interface=_undefined, const=_undefined, annotation=_undefined):
        if file is not _undefined:
            self._assert_undefined(struct, "struct", "file")
            self._assert_undefined(enum, "enum", "file")
            self._assert_undefined(interface, "interface", "file")
            self._assert_undefined(const, "const", "file")
            self._assert_undefined(annotation, "annotation", "file")
            buf = self.__new_file(id=id, displayName=displayName, displayNamePrefixLength=displayNamePrefixLength, scopeId=scopeId, nestedNodes=nestedNodes, annotations=annotations, parameters=parameters, isGeneric=isGeneric, file=file)
            _Struct.__init__(self, buf, 0, 5, 6)
            return
        if struct is not _undefined:
            self._assert_undefined(file, "file", "struct")
            self._assert_undefined(enum, "enum", "struct")
            self._assert_undefined(interface, "interface", "struct")
            self._assert_undefined(const, "const", "struct")
            self._assert_undefined(annotation, "annotation", "struct")
            buf = self.__new_struct(id=id, displayName=displayName, displayNamePrefixLength=displayNamePrefixLength, scopeId=scopeId, nestedNodes=nestedNodes, annotations=annotations, parameters=parameters, isGeneric=isGeneric, struct=struct)
            _Struct.__init__(self, buf, 0, 5, 6)
            return
        if enum is not _undefined:
            self._assert_undefined(file, "file", "enum")
            self._assert_undefined(struct, "struct", "enum")
            self._assert_undefined(interface, "interface", "enum")
            self._assert_undefined(const, "const", "enum")
            self._assert_undefined(annotation, "annotation", "enum")
            buf = self.__new_enum(id=id, displayName=displayName, displayNamePrefixLength=displayNamePrefixLength, scopeId=scopeId, nestedNodes=nestedNodes, annotations=annotations, parameters=parameters, isGeneric=isGeneric, enum=enum)
            _Struct.__init__(self, buf, 0, 5, 6)
            return
        if interface is not _undefined:
            self._assert_undefined(file, "file", "interface")
            self._assert_undefined(struct, "struct", "interface")
            self._assert_undefined(enum, "enum", "interface")
            self._assert_undefined(const, "const", "interface")
            self._assert_undefined(annotation, "annotation", "interface")
            buf = self.__new_interface(id=id, displayName=displayName, displayNamePrefixLength=displayNamePrefixLength, scopeId=scopeId, nestedNodes=nestedNodes, annotations=annotations, parameters=parameters, isGeneric=isGeneric, interface=interface)
            _Struct.__init__(self, buf, 0, 5, 6)
            return
        if const is not _undefined:
            self._assert_undefined(file, "file", "const")
            self._assert_undefined(struct, "struct", "const")
            self._assert_undefined(enum, "enum", "const")
            self._assert_undefined(interface, "interface", "const")
            self._assert_undefined(annotation, "annotation", "const")
            buf = self.__new_const(id=id, displayName=displayName, displayNamePrefixLength=displayNamePrefixLength, scopeId=scopeId, nestedNodes=nestedNodes, annotations=annotations, parameters=parameters, isGeneric=isGeneric, const=const)
            _Struct.__init__(self, buf, 0, 5, 6)
            return
        if annotation is not _undefined:
            self._assert_undefined(file, "file", "annotation")
            self._assert_undefined(struct, "struct", "annotation")
            self._assert_undefined(enum, "enum", "annotation")
            self._assert_undefined(interface, "interface", "annotation")
            self._assert_undefined(const, "const", "annotation")
            buf = self.__new_annotation(id=id, displayName=displayName, displayNamePrefixLength=displayNamePrefixLength, scopeId=scopeId, nestedNodes=nestedNodes, annotations=annotations, parameters=parameters, isGeneric=isGeneric, annotation=annotation)
            _Struct.__init__(self, buf, 0, 5, 6)
            return
        raise TypeError("one of the following args is required: file, struct, enum, interface, const, annotation")
    
    def shortrepr(self):
        parts = [
            "(",
            "id = ", str(self.id), ", ",
            "displayName = ", str(self.displayName), ", ",
            "displayNamePrefixLength = ", str(self.displayNamePrefixLength), ", ",
            "scopeId = ", str(self.scopeId), ", ",
            "nestedNodes = ", str(self.nestedNodes), ", ",
            "annotations = ", str(self.annotations), ", ",
            "file = ", str(self.file), ", ",
            "struct = ", str(self.struct), ", ",
            "enum = ", str(self.enum), ", ",
            "interface = ", str(self.interface), ", ",
            "const = ", str(self.const), ", ",
            "annotation = ", str(self.annotation), ", ",
            "parameters = ", str(self.parameters), ", ",
            "isGeneric = ", str(self.isGeneric), 
            ")"
            ]
        return "".join(parts)



del globals()['CodeGeneratorRequest_RequestedFile']
del globals()['CodeGeneratorRequest_RequestedFile_Import']
del globals()['Brand_Binding']
del globals()['Brand_Scope']
del globals()['Node_NestedNode']
del globals()['Node_Parameter']

try:
    import schema_extended # side effects
except ImportError:
    pass
