# THIS FILE HAS BEEN GENERATED AUTOMATICALLY BY capnpy
# do not edit by hand
# generated on 2016-01-15 16:46
# input files: 
#   - capnpy/schema.capnp

from capnpy.struct_ import Struct as _Struct
from capnpy.struct_ import undefined as _undefined
from capnpy import field as _field
from capnpy.enum import enum as _enum
from capnpy.blob import Types as _Types
from capnpy.builder import StructBuilder as _StructBuilder
from capnpy.list import PrimitiveList as _PrimitiveList
from capnpy.list import StructList as _StructList
from capnpy.list import StringList as _StringList
#_c++_capnp = __compiler.load_schema("/capnp/c++.capnp")

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
class Type__group_anyPointer__group_parameter(_Struct): pass
Type__group_anyPointer__group_parameter.__name__ = 'Type._group_anyPointer._group_parameter'
class Type__group_anyPointer__group_implicitMethodParameter(_Struct): pass
Type__group_anyPointer__group_implicitMethodParameter.__name__ = 'Type._group_anyPointer._group_implicitMethodParameter'
class Type__group_anyPointer(_Struct): pass
Type__group_anyPointer.__name__ = 'Type._group_anyPointer'
class Type__group_struct(_Struct): pass
Type__group_struct.__name__ = 'Type._group_struct'
class Type__group_enum(_Struct): pass
Type__group_enum.__name__ = 'Type._group_enum'
class Type__group_interface(_Struct): pass
Type__group_interface.__name__ = 'Type._group_interface'
class Type__group_list(_Struct): pass
Type__group_list.__name__ = 'Type._group_list'
class Type(_Struct): pass
Type.__name__ = 'Type'
class Field__group_group(_Struct): pass
Field__group_group.__name__ = 'Field._group_group'
class Field__group_ordinal(_Struct): pass
Field__group_ordinal.__name__ = 'Field._group_ordinal'
class Field__group_slot(_Struct): pass
Field__group_slot.__name__ = 'Field._group_slot'
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
class Node__group_interface(_Struct): pass
Node__group_interface.__name__ = 'Node._group_interface'
class Node__group_const(_Struct): pass
Node__group_const.__name__ = 'Node._group_const'
class Node__group_struct(_Struct): pass
Node__group_struct.__name__ = 'Node._group_struct'
class Node__group_annotation(_Struct): pass
Node__group_annotation.__name__ = 'Node._group_annotation'
class Node__group_enum(_Struct): pass
Node__group_enum.__name__ = 'Node._group_enum'
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
    id = _field.Primitive("id", 0, _Types.uint64, 0)
    name = _field.String("name", 0)
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
    id = _field.Primitive("id", 0, _Types.uint64, 0)
    filename = _field.String("filename", 0)
    imports = _field.List("imports", 8, CodeGeneratorRequest_RequestedFile_Import)
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
    nodes = _field.List("nodes", 0, Node)
    requestedFiles = _field.List("requestedFiles", 8, CodeGeneratorRequest_RequestedFile)
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
    name = _field.String("name", 0)
    codeOrder = _field.Primitive("codeOrder", 0, _Types.uint16, 0)
    paramStructType = _field.Primitive("paramStructType", 8, _Types.uint64, 0)
    resultStructType = _field.Primitive("resultStructType", 16, _Types.uint64, 0)
    annotations = _field.List("annotations", 8, Annotation)
    paramBrand = _field.Struct("paramBrand", 16, Brand)
    resultBrand = _field.Struct("resultBrand", 24, Brand)
    implicitParameters = _field.List("implicitParameters", 32, Node_Parameter)
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
    name = _field.String("name", 0)
    codeOrder = _field.Primitive("codeOrder", 0, _Types.uint16, 0)
    annotations = _field.List("annotations", 8, Annotation)
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

@Type__group_anyPointer__group_parameter.__extend__
class Type__group_anyPointer__group_parameter(_Struct):
    __static_data_size__ = 3
    __static_ptrs_size__ = 1
    scopeId = _field.Primitive("scopeId", 16, _Types.uint64, 0)
    parameterIndex = _field.Primitive("parameterIndex", 10, _Types.uint16, 0)
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

@Type__group_anyPointer__group_implicitMethodParameter.__extend__
class Type__group_anyPointer__group_implicitMethodParameter(_Struct):
    __static_data_size__ = 3
    __static_ptrs_size__ = 1
    parameterIndex = _field.Primitive("parameterIndex", 10, _Types.uint16, 0)
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

@Type__group_anyPointer.__extend__
class Type__group_anyPointer(_Struct):
    __static_data_size__ = 3
    __static_ptrs_size__ = 1
    _group_parameter = Type__group_anyPointer__group_parameter
    _group_implicitMethodParameter = Type__group_anyPointer__group_implicitMethodParameter
    __tag_offset__ = 8
    __tag__ = _enum('_group_anyPointer.__tag__', ('unconstrained', 'parameter', 'implicitMethodParameter'))
    unconstrained = _field.Void("unconstrained")
    unconstrained = _field.Union(0, unconstrained)
    parameter = _field.Group(Type__group_anyPointer__group_parameter)
    parameter = _field.Union(1, parameter)
    implicitMethodParameter = _field.Group(Type__group_anyPointer__group_implicitMethodParameter)
    implicitMethodParameter = _field.Union(2, implicitMethodParameter)
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

@Type__group_struct.__extend__
class Type__group_struct(_Struct):
    __static_data_size__ = 3
    __static_ptrs_size__ = 1
    typeId = _field.Primitive("typeId", 8, _Types.uint64, 0)
    brand = _field.Struct("brand", 0, Brand)
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

@Type__group_enum.__extend__
class Type__group_enum(_Struct):
    __static_data_size__ = 3
    __static_ptrs_size__ = 1
    typeId = _field.Primitive("typeId", 8, _Types.uint64, 0)
    brand = _field.Struct("brand", 0, Brand)
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

@Type__group_interface.__extend__
class Type__group_interface(_Struct):
    __static_data_size__ = 3
    __static_ptrs_size__ = 1
    typeId = _field.Primitive("typeId", 8, _Types.uint64, 0)
    brand = _field.Struct("brand", 0, Brand)
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

@Type__group_list.__extend__
class Type__group_list(_Struct):
    __static_data_size__ = 3
    __static_ptrs_size__ = 1
    elementType = _field.Struct("elementType", 0, Type)
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
    _group_anyPointer = Type__group_anyPointer
    _group_struct = Type__group_struct
    _group_enum = Type__group_enum
    _group_interface = Type__group_interface
    _group_list = Type__group_list
    __tag_offset__ = 0
    __tag__ = _enum('Type.__tag__', ('void', 'bool', 'int8', 'int16', 'int32', 'int64', 'uint8', 'uint16', 'uint32', 'uint64', 'float32', 'float64', 'text', 'data', 'list', 'enum', 'struct', 'interface', 'anyPointer'))
    void = _field.Void("void")
    void = _field.Union(0, void)
    bool = _field.Void("bool")
    bool = _field.Union(1, bool)
    int8 = _field.Void("int8")
    int8 = _field.Union(2, int8)
    int16 = _field.Void("int16")
    int16 = _field.Union(3, int16)
    int32 = _field.Void("int32")
    int32 = _field.Union(4, int32)
    int64 = _field.Void("int64")
    int64 = _field.Union(5, int64)
    uint8 = _field.Void("uint8")
    uint8 = _field.Union(6, uint8)
    uint16 = _field.Void("uint16")
    uint16 = _field.Union(7, uint16)
    uint32 = _field.Void("uint32")
    uint32 = _field.Union(8, uint32)
    uint64 = _field.Void("uint64")
    uint64 = _field.Union(9, uint64)
    float32 = _field.Void("float32")
    float32 = _field.Union(10, float32)
    float64 = _field.Void("float64")
    float64 = _field.Union(11, float64)
    text = _field.Void("text")
    text = _field.Union(12, text)
    data = _field.Void("data")
    data = _field.Union(13, data)
    list = _field.Group(Type__group_list)
    list = _field.Union(14, list)
    enum = _field.Group(Type__group_enum)
    enum = _field.Union(15, enum)
    struct = _field.Group(Type__group_struct)
    struct = _field.Union(16, struct)
    interface = _field.Group(Type__group_interface)
    interface = _field.Union(17, interface)
    anyPointer = _field.Group(Type__group_anyPointer)
    anyPointer = _field.Union(18, anyPointer)
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

@Field__group_group.__extend__
class Field__group_group(_Struct):
    __static_data_size__ = 3
    __static_ptrs_size__ = 4
    typeId = _field.Primitive("typeId", 16, _Types.uint64, 0)
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

@Field__group_ordinal.__extend__
class Field__group_ordinal(_Struct):
    __static_data_size__ = 3
    __static_ptrs_size__ = 4
    __tag_offset__ = 10
    __tag__ = _enum('_group_ordinal.__tag__', ('implicit', 'explicit'))
    implicit = _field.Void("implicit")
    implicit = _field.Union(0, implicit)
    explicit = _field.Primitive("explicit", 12, _Types.uint16, 0)
    explicit = _field.Union(1, explicit)
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

@Field__group_slot.__extend__
class Field__group_slot(_Struct):
    __static_data_size__ = 3
    __static_ptrs_size__ = 4
    offset = _field.Primitive("offset", 4, _Types.uint32, 0)
    type = _field.Struct("type", 16, Type)
    defaultValue = _field.Struct("defaultValue", 24, Value)
    hadExplicitDefault = _field.Bool("hadExplicitDefault", 16, 0, False)
    @staticmethod
    def __new(*args, **kwargs):
        raise NotImplementedError('Unsupported field type: <capnpy.schema_extended.Field__Slot object at 0x7f43e9c02a90>')
    
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
    _group_group = Field__group_group
    _group_ordinal = Field__group_ordinal
    _group_slot = Field__group_slot
    noDiscriminant = 65535
    __tag_offset__ = 8
    __tag__ = _enum('Field.__tag__', ('slot', 'group'))
    name = _field.String("name", 0)
    codeOrder = _field.Primitive("codeOrder", 0, _Types.uint16, 0)
    annotations = _field.List("annotations", 8, Annotation)
    discriminantValue = _field.Primitive("discriminantValue", 2, _Types.uint16, 65535)
    slot = _field.Group(Field__group_slot)
    slot = _field.Union(0, slot)
    group = _field.Group(Field__group_group)
    group = _field.Union(1, group)
    ordinal = _field.Group(Field__group_ordinal)
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
    id = _field.Primitive("id", 0, _Types.uint64, 0)
    brand = _field.Struct("brand", 0, Brand)
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
    void = _field.Void("void")
    void = _field.Union(0, void)
    bool = _field.Bool("bool", 2, 0, False)
    bool = _field.Union(1, bool)
    int8 = _field.Primitive("int8", 2, _Types.int8, 0)
    int8 = _field.Union(2, int8)
    int16 = _field.Primitive("int16", 2, _Types.int16, 0)
    int16 = _field.Union(3, int16)
    int32 = _field.Primitive("int32", 4, _Types.int32, 0)
    int32 = _field.Union(4, int32)
    int64 = _field.Primitive("int64", 8, _Types.int64, 0)
    int64 = _field.Union(5, int64)
    uint8 = _field.Primitive("uint8", 2, _Types.uint8, 0)
    uint8 = _field.Union(6, uint8)
    uint16 = _field.Primitive("uint16", 2, _Types.uint16, 0)
    uint16 = _field.Union(7, uint16)
    uint32 = _field.Primitive("uint32", 4, _Types.uint32, 0)
    uint32 = _field.Union(8, uint32)
    uint64 = _field.Primitive("uint64", 8, _Types.uint64, 0)
    uint64 = _field.Union(9, uint64)
    float32 = _field.Primitive("float32", 4, _Types.float32, 0.0)
    float32 = _field.Union(10, float32)
    float64 = _field.Primitive("float64", 8, _Types.float64, 0.0)
    float64 = _field.Union(11, float64)
    text = _field.String("text", 0)
    text = _field.Union(12, text)
    data = _field.Data("data", 0)
    data = _field.Union(13, data)
    list = _field.AnyPointer("list", 0)
    list = _field.Union(14, list)
    enum = _field.Primitive("enum", 2, _Types.uint16, 0)
    enum = _field.Union(15, enum)
    struct = _field.AnyPointer("struct", 0)
    struct = _field.Union(16, struct)
    interface = _field.Void("interface")
    interface = _field.Union(17, interface)
    anyPointer = _field.AnyPointer("anyPointer", 0)
    anyPointer = _field.Union(18, anyPointer)
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
        raise NotImplementedError('Unsupported field type: <capnpy.schema_extended.Field__Slot object at 0x7f43e9c18a10>')
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
        raise NotImplementedError('Unsupported field type: <capnpy.schema_extended.Field__Slot object at 0x7f43e9c18c50>')
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
        raise NotImplementedError('Unsupported field type: <capnpy.schema_extended.Field__Slot object at 0x7f43e9c18c90>')
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
        raise NotImplementedError('Unsupported field type: <capnpy.schema_extended.Field__Slot object at 0x7f43e9c18d10>')
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
        raise NotImplementedError('Unsupported field type: <capnpy.schema_extended.Field__Slot object at 0x7f43e9c18d90>')
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
    unbound = _field.Void("unbound")
    unbound = _field.Union(0, unbound)
    type = _field.Struct("type", 0, Type)
    type = _field.Union(1, type)
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
    scopeId = _field.Primitive("scopeId", 0, _Types.uint64, 0)
    bind = _field.List("bind", 0, Brand_Binding)
    bind = _field.Union(0, bind)
    inherit = _field.Void("inherit")
    inherit = _field.Union(1, inherit)
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
    scopes = _field.List("scopes", 0, Brand_Scope)
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
    id = _field.Primitive("id", 0, _Types.uint64, 0)
    value = _field.Struct("value", 0, Value)
    brand = _field.Struct("brand", 8, Brand)
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

@Node__group_interface.__extend__
class Node__group_interface(_Struct):
    __static_data_size__ = 5
    __static_ptrs_size__ = 6
    methods = _field.List("methods", 24, Method)
    superclasses = _field.List("superclasses", 32, Superclass)
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

@Node__group_const.__extend__
class Node__group_const(_Struct):
    __static_data_size__ = 5
    __static_ptrs_size__ = 6
    type = _field.Struct("type", 24, Type)
    value = _field.Struct("value", 32, Value)
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

@Node__group_struct.__extend__
class Node__group_struct(_Struct):
    __static_data_size__ = 5
    __static_ptrs_size__ = 6
    dataWordCount = _field.Primitive("dataWordCount", 14, _Types.uint16, 0)
    pointerCount = _field.Primitive("pointerCount", 24, _Types.uint16, 0)
    preferredListEncoding = _field.Enum("preferredListEncoding", 26, ElementSize)
    isGroup = _field.Bool("isGroup", 28, 0, False)
    discriminantCount = _field.Primitive("discriminantCount", 30, _Types.uint16, 0)
    discriminantOffset = _field.Primitive("discriminantOffset", 32, _Types.uint32, 0)
    fields = _field.List("fields", 24, Field)
    @staticmethod
    def __new(*args, **kwargs):
        raise NotImplementedError('Unsupported field type: <capnpy.schema_extended.Field__Slot object at 0x7f43e9bad890>')
    
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

@Node__group_annotation.__extend__
class Node__group_annotation(_Struct):
    __static_data_size__ = 5
    __static_ptrs_size__ = 6
    type = _field.Struct("type", 24, Type)
    targetsFile = _field.Bool("targetsFile", 14, 0, False)
    targetsConst = _field.Bool("targetsConst", 14, 1, False)
    targetsEnum = _field.Bool("targetsEnum", 14, 2, False)
    targetsEnumerant = _field.Bool("targetsEnumerant", 14, 3, False)
    targetsStruct = _field.Bool("targetsStruct", 14, 4, False)
    targetsField = _field.Bool("targetsField", 14, 5, False)
    targetsUnion = _field.Bool("targetsUnion", 14, 6, False)
    targetsGroup = _field.Bool("targetsGroup", 14, 7, False)
    targetsInterface = _field.Bool("targetsInterface", 15, 0, False)
    targetsMethod = _field.Bool("targetsMethod", 15, 1, False)
    targetsParam = _field.Bool("targetsParam", 15, 2, False)
    targetsAnnotation = _field.Bool("targetsAnnotation", 15, 3, False)
    @staticmethod
    def __new(*args, **kwargs):
        raise NotImplementedError('Unsupported field type: <capnpy.schema_extended.Field__Slot object at 0x7f43e9badb10>')
    
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

@Node__group_enum.__extend__
class Node__group_enum(_Struct):
    __static_data_size__ = 5
    __static_ptrs_size__ = 6
    enumerants = _field.List("enumerants", 24, Enumerant)
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
    name = _field.String("name", 0)
    id = _field.Primitive("id", 0, _Types.uint64, 0)
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
    name = _field.String("name", 0)
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
    _group_interface = Node__group_interface
    _group_const = Node__group_const
    _group_struct = Node__group_struct
    _group_annotation = Node__group_annotation
    _group_enum = Node__group_enum
    NestedNode = Node_NestedNode
    Parameter = Node_Parameter
    __tag_offset__ = 12
    __tag__ = _enum('Node.__tag__', ('file', 'struct', 'enum', 'interface', 'const', 'annotation'))
    id = _field.Primitive("id", 0, _Types.uint64, 0)
    displayName = _field.String("displayName", 0)
    displayNamePrefixLength = _field.Primitive("displayNamePrefixLength", 8, _Types.uint32, 0)
    scopeId = _field.Primitive("scopeId", 16, _Types.uint64, 0)
    nestedNodes = _field.List("nestedNodes", 8, Node_NestedNode)
    annotations = _field.List("annotations", 16, Annotation)
    file = _field.Void("file")
    file = _field.Union(0, file)
    struct = _field.Group(Node__group_struct)
    struct = _field.Union(1, struct)
    enum = _field.Group(Node__group_enum)
    enum = _field.Union(2, enum)
    interface = _field.Group(Node__group_interface)
    interface = _field.Union(3, interface)
    const = _field.Group(Node__group_const)
    const = _field.Union(4, const)
    annotation = _field.Group(Node__group_annotation)
    annotation = _field.Union(5, annotation)
    parameters = _field.List("parameters", 40, Node_Parameter)
    isGeneric = _field.Bool("isGeneric", 36, 0, False)
    @staticmethod
    def __new_file(*args, **kwargs):
        raise NotImplementedError('Unsupported field type: <capnpy.schema_extended.Field__Slot object at 0x7f43e9badfd0>')
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
del globals()['Type__group_anyPointer']
del globals()['Type__group_anyPointer__group_parameter']
del globals()['Type__group_anyPointer__group_implicitMethodParameter']
del globals()['Type__group_struct']
del globals()['Type__group_enum']
del globals()['Type__group_interface']
del globals()['Type__group_list']
del globals()['Field__group_group']
del globals()['Field__group_ordinal']
del globals()['Field__group_slot']
del globals()['Brand_Binding']
del globals()['Brand_Scope']
del globals()['Node__group_interface']
del globals()['Node__group_const']
del globals()['Node__group_struct']
del globals()['Node__group_annotation']
del globals()['Node__group_enum']
del globals()['Node_NestedNode']
del globals()['Node_Parameter']

try:
    import schema_extended # side effects
except ImportError:
    pass
