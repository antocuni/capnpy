# THIS FILE HAS BEEN GENERATED AUTOMATICALLY BY capnpy
# do not edit by hand
# generated on 2016-10-07 11:19

from capnpy.ptr import E_IS_FAR_POINTER as _E_IS_FAR_POINTER
from capnpy.struct_ import Struct as _Struct
from capnpy.struct_ import check_tag as _check_tag
from capnpy.struct_ import undefined as _undefined
from capnpy.enum import enum as _enum
from capnpy.blob import Types as _Types
from capnpy.builder import StructBuilder as _StructBuilder
from capnpy.list import PrimitiveList as _PrimitiveList
from capnpy.list import StructList as _StructList
from capnpy.list import StringList as _StringList
from capnpy.util import text_repr as _text_repr
from capnpy.util import float32_repr as _float32_repr
from capnpy.util import float64_repr as _float64_repr
from capnpy.util import extend_module_maybe as _extend_module_maybe

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

ElementSize = _enum('ElementSize', ['empty', 'bit', 'byte', 'twoBytes', 'fourBytes', 'eightBytes', 'pointer', 'inlineComposite'])

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
    
    def get_name(self):
        return self._read_str_text(0, default_="")
    
    def has_name(self):
        ptr = self._read_fast_ptr(0)
        return ptr != 0
    
    @staticmethod
    def __new(id=0, name=None):
        builder = _StructBuilder('Qq')
        name = builder.alloc_text(8, name)
        buf = builder.build(id, name)
        return buf
    
    def __init__(self, id=0, name=None):
        _buf = self.__new(id, name)
        _Struct.__init__(self, _buf, 0, 1, 1)
    
    def shortrepr(self):
        parts = []
        parts.append("id = %s" % self.id)
        if self.has_name(): parts.append("name = %s" % _text_repr(self.get_name()))
        return "(%s)" % ", ".join(parts)


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
    
    def get_filename(self):
        return self._read_str_text(0, default_="")
    
    def has_filename(self):
        ptr = self._read_fast_ptr(0)
        return ptr != 0
    
    @property
    def imports(self):
        # no union check
        return self._read_list(8, _StructList, CodeGeneratorRequest.RequestedFile.Import)
    
    def get_imports(self):
        res = self.imports
        if res is None:
            return _StructList.from_buffer('', 0, 0, 0, CodeGeneratorRequest.RequestedFile.Import)
        return res
    
    def has_imports(self):
        ptr = self._read_fast_ptr(8)
        return ptr != 0
    
    @staticmethod
    def __new(id=0, filename=None, imports=None):
        builder = _StructBuilder('Qqq')
        filename = builder.alloc_text(8, filename)
        imports = builder.alloc_list(16, _StructList, CodeGeneratorRequest.RequestedFile.Import, imports)
        buf = builder.build(id, filename, imports)
        return buf
    
    def __init__(self, id=0, filename=None, imports=None):
        _buf = self.__new(id, filename, imports)
        _Struct.__init__(self, _buf, 0, 1, 2)
    
    def shortrepr(self):
        parts = []
        parts.append("id = %s" % self.id)
        if self.has_filename(): parts.append("filename = %s" % _text_repr(self.get_filename()))
        if self.has_imports(): parts.append("imports = %s" % self.get_imports().shortrepr())
        return "(%s)" % ", ".join(parts)


@CodeGeneratorRequest.__extend__
class CodeGeneratorRequest(_Struct):
    __static_data_size__ = 0
    __static_ptrs_size__ = 2
    
    RequestedFile = CodeGeneratorRequest_RequestedFile
    
    @property
    def nodes(self):
        # no union check
        return self._read_list(0, _StructList, Node)
    
    def get_nodes(self):
        res = self.nodes
        if res is None:
            return _StructList.from_buffer('', 0, 0, 0, Node)
        return res
    
    def has_nodes(self):
        ptr = self._read_fast_ptr(0)
        return ptr != 0
    
    @property
    def requestedFiles(self):
        # no union check
        return self._read_list(8, _StructList, CodeGeneratorRequest.RequestedFile)
    
    def get_requestedFiles(self):
        res = self.requestedFiles
        if res is None:
            return _StructList.from_buffer('', 0, 0, 0, CodeGeneratorRequest.RequestedFile)
        return res
    
    def has_requestedFiles(self):
        ptr = self._read_fast_ptr(8)
        return ptr != 0
    
    @staticmethod
    def __new(nodes=None, requestedFiles=None):
        builder = _StructBuilder('qq')
        nodes = builder.alloc_list(0, _StructList, Node, nodes)
        requestedFiles = builder.alloc_list(8, _StructList, CodeGeneratorRequest.RequestedFile, requestedFiles)
        buf = builder.build(nodes, requestedFiles)
        return buf
    
    def __init__(self, nodes=None, requestedFiles=None):
        _buf = self.__new(nodes, requestedFiles)
        _Struct.__init__(self, _buf, 0, 0, 2)
    
    def shortrepr(self):
        parts = []
        if self.has_nodes(): parts.append("nodes = %s" % self.get_nodes().shortrepr())
        if self.has_requestedFiles(): parts.append("requestedFiles = %s" % self.get_requestedFiles().shortrepr())
        return "(%s)" % ", ".join(parts)


@Method.__extend__
class Method(_Struct):
    __static_data_size__ = 3
    __static_ptrs_size__ = 5
    
    
    @property
    def name(self):
        # no union check
        return self._read_str_text(0)
    
    def get_name(self):
        return self._read_str_text(0, default_="")
    
    def has_name(self):
        ptr = self._read_fast_ptr(0)
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
    
    def get_annotations(self):
        res = self.annotations
        if res is None:
            return _StructList.from_buffer('', 0, 0, 0, Annotation)
        return res
    
    def has_annotations(self):
        ptr = self._read_fast_ptr(8)
        return ptr != 0
    
    @property
    def paramBrand(self):
        # no union check
        offset = 16
        p = self._read_fast_ptr(offset)
        if p == _E_IS_FAR_POINTER:
            offset, p = self._read_far_ptr(offset)
        else:
            offset += self._ptrs_offset
        if p == 0:
            return None
        obj = Brand.__new__(Brand)
        obj._init_from_pointer(self._buf, offset, p)
        return obj
    
    def get_paramBrand(self):
        res = self.paramBrand
        if res is None:
            return Brand.from_buffer('', 0, data_size=0, ptrs_size=0)
        return res
    
    def has_paramBrand(self):
        ptr = self._read_fast_ptr(16)
        return ptr != 0
    
    @property
    def resultBrand(self):
        # no union check
        offset = 24
        p = self._read_fast_ptr(offset)
        if p == _E_IS_FAR_POINTER:
            offset, p = self._read_far_ptr(offset)
        else:
            offset += self._ptrs_offset
        if p == 0:
            return None
        obj = Brand.__new__(Brand)
        obj._init_from_pointer(self._buf, offset, p)
        return obj
    
    def get_resultBrand(self):
        res = self.resultBrand
        if res is None:
            return Brand.from_buffer('', 0, data_size=0, ptrs_size=0)
        return res
    
    def has_resultBrand(self):
        ptr = self._read_fast_ptr(24)
        return ptr != 0
    
    @property
    def implicitParameters(self):
        # no union check
        return self._read_list(32, _StructList, Node.Parameter)
    
    def get_implicitParameters(self):
        res = self.implicitParameters
        if res is None:
            return _StructList.from_buffer('', 0, 0, 0, Node.Parameter)
        return res
    
    def has_implicitParameters(self):
        ptr = self._read_fast_ptr(32)
        return ptr != 0
    
    @staticmethod
    def __new(name=None, codeOrder=0, paramStructType=0, resultStructType=0, annotations=None, paramBrand=None, resultBrand=None, implicitParameters=None):
        builder = _StructBuilder('HxxxxxxQQqqqqq')
        name = builder.alloc_text(24, name)
        annotations = builder.alloc_list(32, _StructList, Annotation, annotations)
        paramBrand = builder.alloc_struct(40, Brand, paramBrand)
        resultBrand = builder.alloc_struct(48, Brand, resultBrand)
        implicitParameters = builder.alloc_list(56, _StructList, Node.Parameter, implicitParameters)
        buf = builder.build(codeOrder, paramStructType, resultStructType, name, annotations, paramBrand, resultBrand, implicitParameters)
        return buf
    
    def __init__(self, name=None, codeOrder=0, paramStructType=0, resultStructType=0, annotations=None, paramBrand=None, resultBrand=None, implicitParameters=None):
        _buf = self.__new(name, codeOrder, paramStructType, resultStructType, annotations, paramBrand, resultBrand, implicitParameters)
        _Struct.__init__(self, _buf, 0, 3, 5)
    
    def shortrepr(self):
        parts = []
        if self.has_name(): parts.append("name = %s" % _text_repr(self.get_name()))
        parts.append("codeOrder = %s" % self.codeOrder)
        parts.append("paramStructType = %s" % self.paramStructType)
        parts.append("resultStructType = %s" % self.resultStructType)
        if self.has_annotations(): parts.append("annotations = %s" % self.get_annotations().shortrepr())
        if self.has_paramBrand(): parts.append("paramBrand = %s" % self.get_paramBrand().shortrepr())
        if self.has_resultBrand(): parts.append("resultBrand = %s" % self.get_resultBrand().shortrepr())
        if self.has_implicitParameters(): parts.append("implicitParameters = %s" % self.get_implicitParameters().shortrepr())
        return "(%s)" % ", ".join(parts)


@Enumerant.__extend__
class Enumerant(_Struct):
    __static_data_size__ = 1
    __static_ptrs_size__ = 2
    
    
    @property
    def name(self):
        # no union check
        return self._read_str_text(0)
    
    def get_name(self):
        return self._read_str_text(0, default_="")
    
    def has_name(self):
        ptr = self._read_fast_ptr(0)
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
    
    def get_annotations(self):
        res = self.annotations
        if res is None:
            return _StructList.from_buffer('', 0, 0, 0, Annotation)
        return res
    
    def has_annotations(self):
        ptr = self._read_fast_ptr(8)
        return ptr != 0
    
    @staticmethod
    def __new(name=None, codeOrder=0, annotations=None):
        builder = _StructBuilder('Hxxxxxxqq')
        name = builder.alloc_text(8, name)
        annotations = builder.alloc_list(16, _StructList, Annotation, annotations)
        buf = builder.build(codeOrder, name, annotations)
        return buf
    
    def __init__(self, name=None, codeOrder=0, annotations=None):
        _buf = self.__new(name, codeOrder, annotations)
        _Struct.__init__(self, _buf, 0, 1, 2)
    
    def shortrepr(self):
        parts = []
        if self.has_name(): parts.append("name = %s" % _text_repr(self.get_name()))
        parts.append("codeOrder = %s" % self.codeOrder)
        if self.has_annotations(): parts.append("annotations = %s" % self.get_annotations().shortrepr())
        return "(%s)" % ", ".join(parts)


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
    
    def shortrepr(self):
        parts = []
        parts.append("scopeId = %s" % self.scopeId)
        parts.append("parameterIndex = %s" % self.parameterIndex)
        return "(%s)" % ", ".join(parts)


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
    
    def shortrepr(self):
        parts = []
        parts.append("parameterIndex = %s" % self.parameterIndex)
        return "(%s)" % ", ".join(parts)


@Type_anyPointer.__extend__
class Type_anyPointer(_Struct):
    __static_data_size__ = 3
    __static_ptrs_size__ = 1
    
    
    __tag_offset__ = 8
    __tag__ = _enum('anyPointer.__tag__', ['unconstrained', 'parameter', 'implicitMethodParameter'])
    
    def is_unconstrained(self):
        return self._read_data_int16(8) == 0
    def is_parameter(self):
        return self._read_data_int16(8) == 1
    def is_implicitMethodParameter(self):
        return self._read_data_int16(8) == 2
    
    @property
    def unconstrained(self):
        self._ensure_union(0)
        return None
    
    @property
    def parameter(self):
        self._ensure_union(1)
        obj = Type_anyPointer_parameter.__new__(Type_anyPointer_parameter)
        _Struct._init_from_buffer(obj, self._buf, self._data_offset,
                                  self._data_size, self._ptrs_size)
        return obj
    
    @staticmethod
    def Parameter(scopeId=0, parameterIndex=0):
        return scopeId, parameterIndex,
    
    @property
    def implicitMethodParameter(self):
        self._ensure_union(2)
        obj = Type_anyPointer_implicitMethodParameter.__new__(Type_anyPointer_implicitMethodParameter)
        _Struct._init_from_buffer(obj, self._buf, self._data_offset,
                                  self._data_size, self._ptrs_size)
        return obj
    
    @staticmethod
    def Implicitmethodparameter(parameterIndex=0):
        return parameterIndex,
    
    def shortrepr(self):
        parts = []
        if self.is_unconstrained(): parts.append("unconstrained = %s" % "void")
        if self.is_parameter(): parts.append("parameter = %s" % self.parameter.shortrepr())
        if self.is_implicitMethodParameter(): parts.append("implicitMethodParameter = %s" % self.implicitMethodParameter.shortrepr())
        return "(%s)" % ", ".join(parts)


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
        offset = 0
        p = self._read_fast_ptr(offset)
        if p == _E_IS_FAR_POINTER:
            offset, p = self._read_far_ptr(offset)
        else:
            offset += self._ptrs_offset
        if p == 0:
            return None
        obj = Brand.__new__(Brand)
        obj._init_from_pointer(self._buf, offset, p)
        return obj
    
    def get_brand(self):
        res = self.brand
        if res is None:
            return Brand.from_buffer('', 0, data_size=0, ptrs_size=0)
        return res
    
    def has_brand(self):
        ptr = self._read_fast_ptr(0)
        return ptr != 0
    
    def shortrepr(self):
        parts = []
        parts.append("typeId = %s" % self.typeId)
        if self.has_brand(): parts.append("brand = %s" % self.get_brand().shortrepr())
        return "(%s)" % ", ".join(parts)


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
        offset = 0
        p = self._read_fast_ptr(offset)
        if p == _E_IS_FAR_POINTER:
            offset, p = self._read_far_ptr(offset)
        else:
            offset += self._ptrs_offset
        if p == 0:
            return None
        obj = Brand.__new__(Brand)
        obj._init_from_pointer(self._buf, offset, p)
        return obj
    
    def get_brand(self):
        res = self.brand
        if res is None:
            return Brand.from_buffer('', 0, data_size=0, ptrs_size=0)
        return res
    
    def has_brand(self):
        ptr = self._read_fast_ptr(0)
        return ptr != 0
    
    def shortrepr(self):
        parts = []
        parts.append("typeId = %s" % self.typeId)
        if self.has_brand(): parts.append("brand = %s" % self.get_brand().shortrepr())
        return "(%s)" % ", ".join(parts)


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
        offset = 0
        p = self._read_fast_ptr(offset)
        if p == _E_IS_FAR_POINTER:
            offset, p = self._read_far_ptr(offset)
        else:
            offset += self._ptrs_offset
        if p == 0:
            return None
        obj = Brand.__new__(Brand)
        obj._init_from_pointer(self._buf, offset, p)
        return obj
    
    def get_brand(self):
        res = self.brand
        if res is None:
            return Brand.from_buffer('', 0, data_size=0, ptrs_size=0)
        return res
    
    def has_brand(self):
        ptr = self._read_fast_ptr(0)
        return ptr != 0
    
    def shortrepr(self):
        parts = []
        parts.append("typeId = %s" % self.typeId)
        if self.has_brand(): parts.append("brand = %s" % self.get_brand().shortrepr())
        return "(%s)" % ", ".join(parts)


@Type_list.__extend__
class Type_list(_Struct):
    __static_data_size__ = 3
    __static_ptrs_size__ = 1
    
    
    @property
    def elementType(self):
        # no union check
        offset = 0
        p = self._read_fast_ptr(offset)
        if p == _E_IS_FAR_POINTER:
            offset, p = self._read_far_ptr(offset)
        else:
            offset += self._ptrs_offset
        if p == 0:
            return None
        obj = Type.__new__(Type)
        obj._init_from_pointer(self._buf, offset, p)
        return obj
    
    def get_elementType(self):
        res = self.elementType
        if res is None:
            return Type.from_buffer('', 0, data_size=0, ptrs_size=0)
        return res
    
    def has_elementType(self):
        ptr = self._read_fast_ptr(0)
        return ptr != 0
    
    def shortrepr(self):
        parts = []
        if self.has_elementType(): parts.append("elementType = %s" % self.get_elementType().shortrepr())
        return "(%s)" % ", ".join(parts)


@Type.__extend__
class Type(_Struct):
    __static_data_size__ = 3
    __static_ptrs_size__ = 1
    
    
    __tag_offset__ = 0
    __tag__ = _enum('Type.__tag__', ['void', 'bool', 'int8', 'int16', 'int32', 'int64', 'uint8', 'uint16', 'uint32', 'uint64', 'float32', 'float64', 'text', 'data', 'list', 'enum', 'struct', 'interface', 'anyPointer'])
    
    def is_void(self):
        return self._read_data_int16(0) == 0
    def is_bool(self):
        return self._read_data_int16(0) == 1
    def is_int8(self):
        return self._read_data_int16(0) == 2
    def is_int16(self):
        return self._read_data_int16(0) == 3
    def is_int32(self):
        return self._read_data_int16(0) == 4
    def is_int64(self):
        return self._read_data_int16(0) == 5
    def is_uint8(self):
        return self._read_data_int16(0) == 6
    def is_uint16(self):
        return self._read_data_int16(0) == 7
    def is_uint32(self):
        return self._read_data_int16(0) == 8
    def is_uint64(self):
        return self._read_data_int16(0) == 9
    def is_float32(self):
        return self._read_data_int16(0) == 10
    def is_float64(self):
        return self._read_data_int16(0) == 11
    def is_text(self):
        return self._read_data_int16(0) == 12
    def is_data(self):
        return self._read_data_int16(0) == 13
    def is_list(self):
        return self._read_data_int16(0) == 14
    def is_enum(self):
        return self._read_data_int16(0) == 15
    def is_struct(self):
        return self._read_data_int16(0) == 16
    def is_interface(self):
        return self._read_data_int16(0) == 17
    def is_anyPointer(self):
        return self._read_data_int16(0) == 18
    
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
        obj = Type_list.__new__(Type_list)
        _Struct._init_from_buffer(obj, self._buf, self._data_offset,
                                  self._data_size, self._ptrs_size)
        return obj
    
    @staticmethod
    def List(elementType=None):
        return elementType,
    
    @property
    def enum(self):
        self._ensure_union(15)
        obj = Type_enum.__new__(Type_enum)
        _Struct._init_from_buffer(obj, self._buf, self._data_offset,
                                  self._data_size, self._ptrs_size)
        return obj
    
    @staticmethod
    def Enum(typeId=0, brand=None):
        return typeId, brand,
    
    @property
    def struct(self):
        self._ensure_union(16)
        obj = Type_struct.__new__(Type_struct)
        _Struct._init_from_buffer(obj, self._buf, self._data_offset,
                                  self._data_size, self._ptrs_size)
        return obj
    
    @staticmethod
    def Struct(typeId=0, brand=None):
        return typeId, brand,
    
    @property
    def interface(self):
        self._ensure_union(17)
        obj = Type_interface.__new__(Type_interface)
        _Struct._init_from_buffer(obj, self._buf, self._data_offset,
                                  self._data_size, self._ptrs_size)
        return obj
    
    @staticmethod
    def Interface(typeId=0, brand=None):
        return typeId, brand,
    
    @property
    def anyPointer(self):
        self._ensure_union(18)
        obj = Type_anyPointer.__new__(Type_anyPointer)
        _Struct._init_from_buffer(obj, self._buf, self._data_offset,
                                  self._data_size, self._ptrs_size)
        return obj
    
    @staticmethod
    def Anypointer(parameter=(0, 0,), implicitMethodParameter=(0,)):
        return parameter, implicitMethodParameter,
    
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
    def __new_list(list=(None,)):
        builder = _StructBuilder('hxxxxxxxxxxxxxxxxxxxxxxq')
        __which__ = 14
        list_elementType, = list
        list_elementType = builder.alloc_struct(24, Type, list_elementType)
        buf = builder.build(__which__, list_elementType)
        return buf
    @classmethod
    def new_list(cls, list=(None,)):
        buf = cls.__new_list(list)
        return cls.from_buffer(buf, 0, 3, 1)
    
    @staticmethod
    def __new_enum(enum=(0, None,)):
        builder = _StructBuilder('hxxxxxxQxxxxxxxxq')
        __which__ = 15
        enum_typeId, enum_brand, = enum
        enum_brand = builder.alloc_struct(24, Brand, enum_brand)
        buf = builder.build(__which__, enum_typeId, enum_brand)
        return buf
    @classmethod
    def new_enum(cls, enum=(0, None,)):
        buf = cls.__new_enum(enum)
        return cls.from_buffer(buf, 0, 3, 1)
    
    @staticmethod
    def __new_struct(struct=(0, None,)):
        builder = _StructBuilder('hxxxxxxQxxxxxxxxq')
        __which__ = 16
        struct_typeId, struct_brand, = struct
        struct_brand = builder.alloc_struct(24, Brand, struct_brand)
        buf = builder.build(__which__, struct_typeId, struct_brand)
        return buf
    @classmethod
    def new_struct(cls, struct=(0, None,)):
        buf = cls.__new_struct(struct)
        return cls.from_buffer(buf, 0, 3, 1)
    
    @staticmethod
    def __new_interface(interface=(0, None,)):
        builder = _StructBuilder('hxxxxxxQxxxxxxxxq')
        __which__ = 17
        interface_typeId, interface_brand, = interface
        interface_brand = builder.alloc_struct(24, Brand, interface_brand)
        buf = builder.build(__which__, interface_typeId, interface_brand)
        return buf
    @classmethod
    def new_interface(cls, interface=(0, None,)):
        buf = cls.__new_interface(interface)
        return cls.from_buffer(buf, 0, 3, 1)
    
    @staticmethod
    def __new_anyPointer(anyPointer=((0, 0,), (0,),)):
        builder = _StructBuilder('hxxxxxxxxHxxxxQxxxxxxxx')
        __which__ = 18
        anyPointer_parameter, anyPointer_implicitMethodParameter, = anyPointer
        anyPointer_parameter_scopeId, anyPointer_parameter_parameterIndex, = anyPointer_parameter
        anyPointer_implicitMethodParameter_parameterIndex, = anyPointer_implicitMethodParameter
        buf = builder.build(__which__, anyPointer_parameter_parameterIndex, anyPointer_implicitMethodParameter_parameterIndex, anyPointer_parameter_scopeId)
        return buf
    @classmethod
    def new_anyPointer(cls, anyPointer=((0, 0,), (0,),)):
        buf = cls.__new_anyPointer(anyPointer)
        return cls.from_buffer(buf, 0, 3, 1)
    
    def __init__(self, void=_undefined, bool=_undefined, int8=_undefined, int16=_undefined, int32=_undefined, int64=_undefined, uint8=_undefined, uint16=_undefined, uint32=_undefined, uint64=_undefined, float32=_undefined, float64=_undefined, text=_undefined, data=_undefined, list=(None,), enum=(0, None,), struct=(0, None,), interface=(0, None,), anyPointer=(_undefined, (0, 0,), (0,),)):
        _buf = None
        _curtag = None
        if void is not _undefined:
            _curtag = _check_tag(_curtag, 'void')
            _buf = self.__new_void()
        if bool is not _undefined:
            _curtag = _check_tag(_curtag, 'bool')
            _buf = self.__new_bool()
        if int8 is not _undefined:
            _curtag = _check_tag(_curtag, 'int8')
            _buf = self.__new_int8()
        if int16 is not _undefined:
            _curtag = _check_tag(_curtag, 'int16')
            _buf = self.__new_int16()
        if int32 is not _undefined:
            _curtag = _check_tag(_curtag, 'int32')
            _buf = self.__new_int32()
        if int64 is not _undefined:
            _curtag = _check_tag(_curtag, 'int64')
            _buf = self.__new_int64()
        if uint8 is not _undefined:
            _curtag = _check_tag(_curtag, 'uint8')
            _buf = self.__new_uint8()
        if uint16 is not _undefined:
            _curtag = _check_tag(_curtag, 'uint16')
            _buf = self.__new_uint16()
        if uint32 is not _undefined:
            _curtag = _check_tag(_curtag, 'uint32')
            _buf = self.__new_uint32()
        if uint64 is not _undefined:
            _curtag = _check_tag(_curtag, 'uint64')
            _buf = self.__new_uint64()
        if float32 is not _undefined:
            _curtag = _check_tag(_curtag, 'float32')
            _buf = self.__new_float32()
        if float64 is not _undefined:
            _curtag = _check_tag(_curtag, 'float64')
            _buf = self.__new_float64()
        if text is not _undefined:
            _curtag = _check_tag(_curtag, 'text')
            _buf = self.__new_text()
        if data is not _undefined:
            _curtag = _check_tag(_curtag, 'data')
            _buf = self.__new_data()
        if list is not _undefined:
            _curtag = _check_tag(_curtag, 'list')
            _buf = self.__new_list(list)
        if enum is not _undefined:
            _curtag = _check_tag(_curtag, 'enum')
            _buf = self.__new_enum(enum)
        if struct is not _undefined:
            _curtag = _check_tag(_curtag, 'struct')
            _buf = self.__new_struct(struct)
        if interface is not _undefined:
            _curtag = _check_tag(_curtag, 'interface')
            _buf = self.__new_interface(interface)
        if anyPointer is not _undefined:
            _curtag = _check_tag(_curtag, 'anyPointer')
            _buf = self.__new_anyPointer(anyPointer)
        if _buf is None:
            raise TypeError("one of the following args is required: void, bool, int8, int16, int32, int64, uint8, uint16, uint32, uint64, float32, float64, text, data, list, enum, struct, interface, anyPointer")
        _Struct.__init__(self, _buf, 0, 3, 1)
    
    def shortrepr(self):
        parts = []
        if self.is_void(): parts.append("void = %s" % "void")
        if self.is_bool(): parts.append("bool = %s" % "void")
        if self.is_int8(): parts.append("int8 = %s" % "void")
        if self.is_int16(): parts.append("int16 = %s" % "void")
        if self.is_int32(): parts.append("int32 = %s" % "void")
        if self.is_int64(): parts.append("int64 = %s" % "void")
        if self.is_uint8(): parts.append("uint8 = %s" % "void")
        if self.is_uint16(): parts.append("uint16 = %s" % "void")
        if self.is_uint32(): parts.append("uint32 = %s" % "void")
        if self.is_uint64(): parts.append("uint64 = %s" % "void")
        if self.is_float32(): parts.append("float32 = %s" % "void")
        if self.is_float64(): parts.append("float64 = %s" % "void")
        if self.is_text(): parts.append("text = %s" % "void")
        if self.is_data(): parts.append("data = %s" % "void")
        if self.is_list(): parts.append("list = %s" % self.list.shortrepr())
        if self.is_enum(): parts.append("enum = %s" % self.enum.shortrepr())
        if self.is_struct(): parts.append("struct = %s" % self.struct.shortrepr())
        if self.is_interface(): parts.append("interface = %s" % self.interface.shortrepr())
        if self.is_anyPointer(): parts.append("anyPointer = %s" % self.anyPointer.shortrepr())
        return "(%s)" % ", ".join(parts)


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
    
    def shortrepr(self):
        parts = []
        parts.append("typeId = %s" % self.typeId)
        return "(%s)" % ", ".join(parts)


@Field_ordinal.__extend__
class Field_ordinal(_Struct):
    __static_data_size__ = 3
    __static_ptrs_size__ = 4
    
    
    __tag_offset__ = 10
    __tag__ = _enum('ordinal.__tag__', ['implicit', 'explicit'])
    
    def is_implicit(self):
        return self._read_data_int16(10) == 0
    def is_explicit(self):
        return self._read_data_int16(10) == 1
    
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
    
    def shortrepr(self):
        parts = []
        if self.is_implicit(): parts.append("implicit = %s" % "void")
        if self.is_explicit(): parts.append("explicit = %s" % self.explicit)
        return "(%s)" % ", ".join(parts)


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
        offset = 16
        p = self._read_fast_ptr(offset)
        if p == _E_IS_FAR_POINTER:
            offset, p = self._read_far_ptr(offset)
        else:
            offset += self._ptrs_offset
        if p == 0:
            return None
        obj = Type.__new__(Type)
        obj._init_from_pointer(self._buf, offset, p)
        return obj
    
    def get_type(self):
        res = self.type
        if res is None:
            return Type.from_buffer('', 0, data_size=0, ptrs_size=0)
        return res
    
    def has_type(self):
        ptr = self._read_fast_ptr(16)
        return ptr != 0
    
    @property
    def defaultValue(self):
        # no union check
        offset = 24
        p = self._read_fast_ptr(offset)
        if p == _E_IS_FAR_POINTER:
            offset, p = self._read_far_ptr(offset)
        else:
            offset += self._ptrs_offset
        if p == 0:
            return None
        obj = Value.__new__(Value)
        obj._init_from_pointer(self._buf, offset, p)
        return obj
    
    def get_defaultValue(self):
        res = self.defaultValue
        if res is None:
            return Value.from_buffer('', 0, data_size=0, ptrs_size=0)
        return res
    
    def has_defaultValue(self):
        ptr = self._read_fast_ptr(24)
        return ptr != 0
    
    @property
    def hadExplicitDefault(self):
        # no union check
        value = self._read_bit(16, 1)
        if False != 0:
            value = value ^ False
        return value
    
    def shortrepr(self):
        parts = []
        parts.append("offset = %s" % self.offset)
        if self.has_type(): parts.append("type = %s" % self.get_type().shortrepr())
        if self.has_defaultValue(): parts.append("defaultValue = %s" % self.get_defaultValue().shortrepr())
        parts.append("hadExplicitDefault = %s" % str(self.hadExplicitDefault).lower())
        return "(%s)" % ", ".join(parts)


@Field.__extend__
class Field(_Struct):
    __static_data_size__ = 3
    __static_ptrs_size__ = 4
    
    noDiscriminant = 65535
    
    __tag_offset__ = 8
    __tag__ = _enum('Field.__tag__', ['slot', 'group'])
    
    def is_slot(self):
        return self._read_data_int16(8) == 0
    def is_group(self):
        return self._read_data_int16(8) == 1
    
    @property
    def name(self):
        # no union check
        return self._read_str_text(0)
    
    def get_name(self):
        return self._read_str_text(0, default_="")
    
    def has_name(self):
        ptr = self._read_fast_ptr(0)
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
    
    def get_annotations(self):
        res = self.annotations
        if res is None:
            return _StructList.from_buffer('', 0, 0, 0, Annotation)
        return res
    
    def has_annotations(self):
        ptr = self._read_fast_ptr(8)
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
        obj = Field_slot.__new__(Field_slot)
        _Struct._init_from_buffer(obj, self._buf, self._data_offset,
                                  self._data_size, self._ptrs_size)
        return obj
    
    @staticmethod
    def Slot(offset=0, type=None, defaultValue=None, hadExplicitDefault=False):
        return offset, type, defaultValue, hadExplicitDefault,
    
    @property
    def group(self):
        self._ensure_union(1)
        obj = Field_group.__new__(Field_group)
        _Struct._init_from_buffer(obj, self._buf, self._data_offset,
                                  self._data_size, self._ptrs_size)
        return obj
    
    @staticmethod
    def Group(typeId=0):
        return typeId,
    
    @property
    def ordinal(self):
        # no union check
        obj = Field_ordinal.__new__(Field_ordinal)
        _Struct._init_from_buffer(obj, self._buf, self._data_offset,
                                  self._data_size, self._ptrs_size)
        return obj
    
    @staticmethod
    def Ordinal(explicit=0):
        return explicit,
    
    @staticmethod
    def __new_slot(*args, **kwargs):
        raise NotImplementedError('Unsupported field type: (name = "hadExplicitDefault", codeOrder = 3, discriminantValue = 65535, slot = (offset = 128, type = (bool = void), defaultValue = (bool = false), hadExplicitDefault = false), ordinal = (explicit = 10))')
    @classmethod
    def new_slot(cls):
        buf = cls.__new_slot()
        return cls.from_buffer(buf, 0, 3, 4)
    
    @staticmethod
    def __new_group(name=None, codeOrder=0, annotations=None, discriminantValue=65535, group=(0,), ordinal=(0,)):
        builder = _StructBuilder('HHxxxxhxxHxxQqqxxxxxxxxxxxxxxxx')
        __which__ = 1
        name = builder.alloc_text(24, name)
        annotations = builder.alloc_list(32, _StructList, Annotation, annotations)
        discriminantValue ^= 65535
        group_typeId, = group
        ordinal_explicit, = ordinal
        buf = builder.build(codeOrder, discriminantValue, __which__, ordinal_explicit, group_typeId, name, annotations)
        return buf
    @classmethod
    def new_group(cls, name=None, codeOrder=0, annotations=None, discriminantValue=65535, group=(0,), ordinal=(0,)):
        buf = cls.__new_group(name, codeOrder, annotations, discriminantValue, group, ordinal)
        return cls.from_buffer(buf, 0, 3, 4)
    
    def __init__(self, name=None, codeOrder=0, annotations=None, discriminantValue=65535, slot=(0, None, None, False,), group=(0,), ordinal=(_undefined, _undefined,)):
        _buf = None
        _curtag = None
        if slot is not _undefined:
            _curtag = _check_tag(_curtag, 'slot')
            _buf = self.__new_slot()
        if group is not _undefined:
            _curtag = _check_tag(_curtag, 'group')
            _buf = self.__new_group(name, codeOrder, annotations, discriminantValue, group, ordinal)
        if _buf is None:
            raise TypeError("one of the following args is required: slot, group")
        _Struct.__init__(self, _buf, 0, 3, 4)
    
    def shortrepr(self):
        parts = []
        if self.has_name(): parts.append("name = %s" % _text_repr(self.get_name()))
        parts.append("codeOrder = %s" % self.codeOrder)
        if self.has_annotations(): parts.append("annotations = %s" % self.get_annotations().shortrepr())
        parts.append("discriminantValue = %s" % self.discriminantValue)
        if self.is_slot(): parts.append("slot = %s" % self.slot.shortrepr())
        if self.is_group(): parts.append("group = %s" % self.group.shortrepr())
        parts.append("ordinal = %s" % self.ordinal.shortrepr())
        return "(%s)" % ", ".join(parts)


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
        offset = 0
        p = self._read_fast_ptr(offset)
        if p == _E_IS_FAR_POINTER:
            offset, p = self._read_far_ptr(offset)
        else:
            offset += self._ptrs_offset
        if p == 0:
            return None
        obj = Brand.__new__(Brand)
        obj._init_from_pointer(self._buf, offset, p)
        return obj
    
    def get_brand(self):
        res = self.brand
        if res is None:
            return Brand.from_buffer('', 0, data_size=0, ptrs_size=0)
        return res
    
    def has_brand(self):
        ptr = self._read_fast_ptr(0)
        return ptr != 0
    
    @staticmethod
    def __new(id=0, brand=None):
        builder = _StructBuilder('Qq')
        brand = builder.alloc_struct(8, Brand, brand)
        buf = builder.build(id, brand)
        return buf
    
    def __init__(self, id=0, brand=None):
        _buf = self.__new(id, brand)
        _Struct.__init__(self, _buf, 0, 1, 1)
    
    def shortrepr(self):
        parts = []
        parts.append("id = %s" % self.id)
        if self.has_brand(): parts.append("brand = %s" % self.get_brand().shortrepr())
        return "(%s)" % ", ".join(parts)


@Value.__extend__
class Value(_Struct):
    __static_data_size__ = 2
    __static_ptrs_size__ = 1
    
    
    __tag_offset__ = 0
    __tag__ = _enum('Value.__tag__', ['void', 'bool', 'int8', 'int16', 'int32', 'int64', 'uint8', 'uint16', 'uint32', 'uint64', 'float32', 'float64', 'text', 'data', 'list', 'enum', 'struct', 'interface', 'anyPointer'])
    
    def is_void(self):
        return self._read_data_int16(0) == 0
    def is_bool(self):
        return self._read_data_int16(0) == 1
    def is_int8(self):
        return self._read_data_int16(0) == 2
    def is_int16(self):
        return self._read_data_int16(0) == 3
    def is_int32(self):
        return self._read_data_int16(0) == 4
    def is_int64(self):
        return self._read_data_int16(0) == 5
    def is_uint8(self):
        return self._read_data_int16(0) == 6
    def is_uint16(self):
        return self._read_data_int16(0) == 7
    def is_uint32(self):
        return self._read_data_int16(0) == 8
    def is_uint64(self):
        return self._read_data_int16(0) == 9
    def is_float32(self):
        return self._read_data_int16(0) == 10
    def is_float64(self):
        return self._read_data_int16(0) == 11
    def is_text(self):
        return self._read_data_int16(0) == 12
    def is_data(self):
        return self._read_data_int16(0) == 13
    def is_list(self):
        return self._read_data_int16(0) == 14
    def is_enum(self):
        return self._read_data_int16(0) == 15
    def is_struct(self):
        return self._read_data_int16(0) == 16
    def is_interface(self):
        return self._read_data_int16(0) == 17
    def is_anyPointer(self):
        return self._read_data_int16(0) == 18
    
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
    
    def get_text(self):
        return self._read_str_text(0, default_="")
    
    def has_text(self):
        ptr = self._read_fast_ptr(0)
        return ptr != 0
    
    @property
    def data(self):
        self._ensure_union(13)
        return self._read_str_data(0)
    
    def get_data(self):
        return self._read_str_data(0, default_="")
    
    def has_data(self):
        ptr = self._read_fast_ptr(0)
        return ptr != 0
    
    @property
    def list(self):
        self._ensure_union(14)
        if not self.has_list():
            return None
        raise ValueError("Cannot get fields of type AnyPointer")
    
    def has_list(self):
        ptr = self._read_fast_ptr(0)
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
        if not self.has_struct():
            return None
        raise ValueError("Cannot get fields of type AnyPointer")
    
    def has_struct(self):
        ptr = self._read_fast_ptr(0)
        return ptr != 0
    
    @property
    def interface(self):
        self._ensure_union(17)
        return None
    
    @property
    def anyPointer(self):
        self._ensure_union(18)
        if not self.has_anyPointer():
            return None
        raise ValueError("Cannot get fields of type AnyPointer")
    
    def has_anyPointer(self):
        ptr = self._read_fast_ptr(0)
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
        raise NotImplementedError('Unsupported field type: (name = "bool", codeOrder = 1, discriminantValue = 1, slot = (offset = 16, type = (bool = void), defaultValue = (bool = false), hadExplicitDefault = false), ordinal = (explicit = 1))')
    @classmethod
    def new_bool(cls):
        buf = cls.__new_bool()
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_int8(int8=0):
        builder = _StructBuilder('hbxxxxxxxxxxxxxxxxxxxxx')
        __which__ = 2
        buf = builder.build(__which__, int8)
        return buf
    @classmethod
    def new_int8(cls, int8=0):
        buf = cls.__new_int8(int8)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_int16(int16=0):
        builder = _StructBuilder('hhxxxxxxxxxxxxxxxxxxxx')
        __which__ = 3
        buf = builder.build(__which__, int16)
        return buf
    @classmethod
    def new_int16(cls, int16=0):
        buf = cls.__new_int16(int16)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_int32(int32=0):
        builder = _StructBuilder('hxxixxxxxxxxxxxxxxxx')
        __which__ = 4
        buf = builder.build(__which__, int32)
        return buf
    @classmethod
    def new_int32(cls, int32=0):
        buf = cls.__new_int32(int32)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_int64(int64=0):
        builder = _StructBuilder('hxxxxxxqxxxxxxxx')
        __which__ = 5
        buf = builder.build(__which__, int64)
        return buf
    @classmethod
    def new_int64(cls, int64=0):
        buf = cls.__new_int64(int64)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_uint8(uint8=0):
        builder = _StructBuilder('hBxxxxxxxxxxxxxxxxxxxxx')
        __which__ = 6
        buf = builder.build(__which__, uint8)
        return buf
    @classmethod
    def new_uint8(cls, uint8=0):
        buf = cls.__new_uint8(uint8)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_uint16(uint16=0):
        builder = _StructBuilder('hHxxxxxxxxxxxxxxxxxxxx')
        __which__ = 7
        buf = builder.build(__which__, uint16)
        return buf
    @classmethod
    def new_uint16(cls, uint16=0):
        buf = cls.__new_uint16(uint16)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_uint32(uint32=0):
        builder = _StructBuilder('hxxIxxxxxxxxxxxxxxxx')
        __which__ = 8
        buf = builder.build(__which__, uint32)
        return buf
    @classmethod
    def new_uint32(cls, uint32=0):
        buf = cls.__new_uint32(uint32)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_uint64(uint64=0):
        builder = _StructBuilder('hxxxxxxQxxxxxxxx')
        __which__ = 9
        buf = builder.build(__which__, uint64)
        return buf
    @classmethod
    def new_uint64(cls, uint64=0):
        buf = cls.__new_uint64(uint64)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_float32(float32=0.0):
        builder = _StructBuilder('hxxfxxxxxxxxxxxxxxxx')
        __which__ = 10
        buf = builder.build(__which__, float32)
        return buf
    @classmethod
    def new_float32(cls, float32=0.0):
        buf = cls.__new_float32(float32)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_float64(float64=0.0):
        builder = _StructBuilder('hxxxxxxdxxxxxxxx')
        __which__ = 11
        buf = builder.build(__which__, float64)
        return buf
    @classmethod
    def new_float64(cls, float64=0.0):
        buf = cls.__new_float64(float64)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_text(text=None):
        builder = _StructBuilder('hxxxxxxxxxxxxxxq')
        __which__ = 12
        text = builder.alloc_text(16, text)
        buf = builder.build(__which__, text)
        return buf
    @classmethod
    def new_text(cls, text=None):
        buf = cls.__new_text(text)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_data(data=None):
        builder = _StructBuilder('hxxxxxxxxxxxxxxq')
        __which__ = 13
        data = builder.alloc_data(16, data)
        buf = builder.build(__which__, data)
        return buf
    @classmethod
    def new_data(cls, data=None):
        buf = cls.__new_data(data)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_list(list=None):
        builder = _StructBuilder('hxxxxxxxxxxxxxxq')
        __which__ = 14
        raise NotImplementedError('Unsupported field type: (name = "list", codeOrder = 14, discriminantValue = 14, slot = (offset = 0, type = (anyPointer = (unconstrained = void)), defaultValue = (anyPointer = ???), hadExplicitDefault = false), ordinal = (explicit = 14))')
        buf = builder.build(__which__, list)
        return buf
    @classmethod
    def new_list(cls, list=None):
        buf = cls.__new_list(list)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_enum(enum=0):
        builder = _StructBuilder('hHxxxxxxxxxxxxxxxxxxxx')
        __which__ = 15
        buf = builder.build(__which__, enum)
        return buf
    @classmethod
    def new_enum(cls, enum=0):
        buf = cls.__new_enum(enum)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_struct(struct=None):
        builder = _StructBuilder('hxxxxxxxxxxxxxxq')
        __which__ = 16
        raise NotImplementedError('Unsupported field type: (name = "struct", codeOrder = 16, discriminantValue = 16, slot = (offset = 0, type = (anyPointer = (unconstrained = void)), defaultValue = (anyPointer = ???), hadExplicitDefault = false), ordinal = (explicit = 16))')
        buf = builder.build(__which__, struct)
        return buf
    @classmethod
    def new_struct(cls, struct=None):
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
    def __new_anyPointer(anyPointer=None):
        builder = _StructBuilder('hxxxxxxxxxxxxxxq')
        __which__ = 18
        raise NotImplementedError('Unsupported field type: (name = "anyPointer", codeOrder = 18, discriminantValue = 18, slot = (offset = 0, type = (anyPointer = (unconstrained = void)), defaultValue = (anyPointer = ???), hadExplicitDefault = false), ordinal = (explicit = 18))')
        buf = builder.build(__which__, anyPointer)
        return buf
    @classmethod
    def new_anyPointer(cls, anyPointer=None):
        buf = cls.__new_anyPointer(anyPointer)
        return cls.from_buffer(buf, 0, 2, 1)
    
    def __init__(self, void=_undefined, bool=_undefined, int8=_undefined, int16=_undefined, int32=_undefined, int64=_undefined, uint8=_undefined, uint16=_undefined, uint32=_undefined, uint64=_undefined, float32=_undefined, float64=_undefined, text=_undefined, data=_undefined, list=_undefined, enum=_undefined, struct=_undefined, interface=_undefined, anyPointer=_undefined):
        _buf = None
        _curtag = None
        if void is not _undefined:
            _curtag = _check_tag(_curtag, 'void')
            _buf = self.__new_void()
        if bool is not _undefined:
            _curtag = _check_tag(_curtag, 'bool')
            _buf = self.__new_bool()
        if int8 is not _undefined:
            _curtag = _check_tag(_curtag, 'int8')
            _buf = self.__new_int8(int8)
        if int16 is not _undefined:
            _curtag = _check_tag(_curtag, 'int16')
            _buf = self.__new_int16(int16)
        if int32 is not _undefined:
            _curtag = _check_tag(_curtag, 'int32')
            _buf = self.__new_int32(int32)
        if int64 is not _undefined:
            _curtag = _check_tag(_curtag, 'int64')
            _buf = self.__new_int64(int64)
        if uint8 is not _undefined:
            _curtag = _check_tag(_curtag, 'uint8')
            _buf = self.__new_uint8(uint8)
        if uint16 is not _undefined:
            _curtag = _check_tag(_curtag, 'uint16')
            _buf = self.__new_uint16(uint16)
        if uint32 is not _undefined:
            _curtag = _check_tag(_curtag, 'uint32')
            _buf = self.__new_uint32(uint32)
        if uint64 is not _undefined:
            _curtag = _check_tag(_curtag, 'uint64')
            _buf = self.__new_uint64(uint64)
        if float32 is not _undefined:
            _curtag = _check_tag(_curtag, 'float32')
            _buf = self.__new_float32(float32)
        if float64 is not _undefined:
            _curtag = _check_tag(_curtag, 'float64')
            _buf = self.__new_float64(float64)
        if text is not _undefined:
            _curtag = _check_tag(_curtag, 'text')
            _buf = self.__new_text(text)
        if data is not _undefined:
            _curtag = _check_tag(_curtag, 'data')
            _buf = self.__new_data(data)
        if list is not _undefined:
            _curtag = _check_tag(_curtag, 'list')
            _buf = self.__new_list(list)
        if enum is not _undefined:
            _curtag = _check_tag(_curtag, 'enum')
            _buf = self.__new_enum(enum)
        if struct is not _undefined:
            _curtag = _check_tag(_curtag, 'struct')
            _buf = self.__new_struct(struct)
        if interface is not _undefined:
            _curtag = _check_tag(_curtag, 'interface')
            _buf = self.__new_interface()
        if anyPointer is not _undefined:
            _curtag = _check_tag(_curtag, 'anyPointer')
            _buf = self.__new_anyPointer(anyPointer)
        if _buf is None:
            raise TypeError("one of the following args is required: void, bool, int8, int16, int32, int64, uint8, uint16, uint32, uint64, float32, float64, text, data, list, enum, struct, interface, anyPointer")
        _Struct.__init__(self, _buf, 0, 2, 1)
    
    def shortrepr(self):
        parts = []
        if self.is_void(): parts.append("void = %s" % "void")
        if self.is_bool(): parts.append("bool = %s" % str(self.bool).lower())
        if self.is_int8(): parts.append("int8 = %s" % self.int8)
        if self.is_int16(): parts.append("int16 = %s" % self.int16)
        if self.is_int32(): parts.append("int32 = %s" % self.int32)
        if self.is_int64(): parts.append("int64 = %s" % self.int64)
        if self.is_uint8(): parts.append("uint8 = %s" % self.uint8)
        if self.is_uint16(): parts.append("uint16 = %s" % self.uint16)
        if self.is_uint32(): parts.append("uint32 = %s" % self.uint32)
        if self.is_uint64(): parts.append("uint64 = %s" % self.uint64)
        if self.is_float32(): parts.append("float32 = %s" % _float32_repr(self.float32))
        if self.is_float64(): parts.append("float64 = %s" % _float64_repr(self.float64))
        if self.is_text() and (self.has_text() or
                                  not False):
            parts.append("text = %s" % _text_repr(self.get_text()))
        if self.is_data() and (self.has_data() or
                                  not False):
            parts.append("data = %s" % _text_repr(self.get_data()))
        if self.is_list() and (self.has_list() or
                                  not False):
            parts.append("list = %s" % "???")
        if self.is_enum(): parts.append("enum = %s" % self.enum)
        if self.is_struct() and (self.has_struct() or
                                  not False):
            parts.append("struct = %s" % "???")
        if self.is_interface(): parts.append("interface = %s" % "void")
        if self.is_anyPointer() and (self.has_anyPointer() or
                                  not False):
            parts.append("anyPointer = %s" % "???")
        return "(%s)" % ", ".join(parts)


@Brand_Binding.__extend__
class Brand_Binding(_Struct):
    __static_data_size__ = 1
    __static_ptrs_size__ = 1
    
    
    __tag_offset__ = 0
    __tag__ = _enum('Binding.__tag__', ['unbound', 'type'])
    
    def is_unbound(self):
        return self._read_data_int16(0) == 0
    def is_type(self):
        return self._read_data_int16(0) == 1
    
    @property
    def unbound(self):
        self._ensure_union(0)
        return None
    
    @property
    def type(self):
        self._ensure_union(1)
        offset = 0
        p = self._read_fast_ptr(offset)
        if p == _E_IS_FAR_POINTER:
            offset, p = self._read_far_ptr(offset)
        else:
            offset += self._ptrs_offset
        if p == 0:
            return None
        obj = Type.__new__(Type)
        obj._init_from_pointer(self._buf, offset, p)
        return obj
    
    def get_type(self):
        res = self.type
        if res is None:
            return Type.from_buffer('', 0, data_size=0, ptrs_size=0)
        return res
    
    def has_type(self):
        ptr = self._read_fast_ptr(0)
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
    def __new_type(type=None):
        builder = _StructBuilder('hxxxxxxq')
        __which__ = 1
        type = builder.alloc_struct(8, Type, type)
        buf = builder.build(__which__, type)
        return buf
    @classmethod
    def new_type(cls, type=None):
        buf = cls.__new_type(type)
        return cls.from_buffer(buf, 0, 1, 1)
    
    def __init__(self, unbound=_undefined, type=_undefined):
        _buf = None
        _curtag = None
        if unbound is not _undefined:
            _curtag = _check_tag(_curtag, 'unbound')
            _buf = self.__new_unbound()
        if type is not _undefined:
            _curtag = _check_tag(_curtag, 'type')
            _buf = self.__new_type(type)
        if _buf is None:
            raise TypeError("one of the following args is required: unbound, type")
        _Struct.__init__(self, _buf, 0, 1, 1)
    
    def shortrepr(self):
        parts = []
        if self.is_unbound(): parts.append("unbound = %s" % "void")
        if self.is_type() and (self.has_type() or
                                  not False):
            parts.append("type = %s" % self.get_type().shortrepr())
        return "(%s)" % ", ".join(parts)


@Brand_Scope.__extend__
class Brand_Scope(_Struct):
    __static_data_size__ = 2
    __static_ptrs_size__ = 1
    
    
    __tag_offset__ = 8
    __tag__ = _enum('Scope.__tag__', ['bind', 'inherit'])
    
    def is_bind(self):
        return self._read_data_int16(8) == 0
    def is_inherit(self):
        return self._read_data_int16(8) == 1
    
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
    
    def get_bind(self):
        res = self.bind
        if res is None:
            return _StructList.from_buffer('', 0, 0, 0, Brand.Binding)
        return res
    
    def has_bind(self):
        ptr = self._read_fast_ptr(0)
        return ptr != 0
    
    @property
    def inherit(self):
        self._ensure_union(1)
        return None
    
    @staticmethod
    def __new_bind(scopeId=0, bind=None):
        builder = _StructBuilder('Qhxxxxxxq')
        __which__ = 0
        bind = builder.alloc_list(16, _StructList, Brand.Binding, bind)
        buf = builder.build(scopeId, __which__, bind)
        return buf
    @classmethod
    def new_bind(cls, scopeId=0, bind=None):
        buf = cls.__new_bind(scopeId, bind)
        return cls.from_buffer(buf, 0, 2, 1)
    
    @staticmethod
    def __new_inherit(scopeId=0):
        builder = _StructBuilder('Qhxxxxxxxxxxxxxx')
        __which__ = 1
        buf = builder.build(scopeId, __which__)
        return buf
    @classmethod
    def new_inherit(cls, scopeId=0):
        buf = cls.__new_inherit(scopeId)
        return cls.from_buffer(buf, 0, 2, 1)
    
    def __init__(self, scopeId=0, bind=_undefined, inherit=_undefined):
        _buf = None
        _curtag = None
        if bind is not _undefined:
            _curtag = _check_tag(_curtag, 'bind')
            _buf = self.__new_bind(scopeId, bind)
        if inherit is not _undefined:
            _curtag = _check_tag(_curtag, 'inherit')
            _buf = self.__new_inherit(scopeId)
        if _buf is None:
            raise TypeError("one of the following args is required: bind, inherit")
        _Struct.__init__(self, _buf, 0, 2, 1)
    
    def shortrepr(self):
        parts = []
        parts.append("scopeId = %s" % self.scopeId)
        if self.is_bind() and (self.has_bind() or
                                  not True):
            parts.append("bind = %s" % self.get_bind().shortrepr())
        if self.is_inherit(): parts.append("inherit = %s" % "void")
        return "(%s)" % ", ".join(parts)


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
    
    def get_scopes(self):
        res = self.scopes
        if res is None:
            return _StructList.from_buffer('', 0, 0, 0, Brand.Scope)
        return res
    
    def has_scopes(self):
        ptr = self._read_fast_ptr(0)
        return ptr != 0
    
    @staticmethod
    def __new(scopes=None):
        builder = _StructBuilder('q')
        scopes = builder.alloc_list(0, _StructList, Brand.Scope, scopes)
        buf = builder.build(scopes)
        return buf
    
    def __init__(self, scopes=None):
        _buf = self.__new(scopes)
        _Struct.__init__(self, _buf, 0, 0, 1)
    
    def shortrepr(self):
        parts = []
        if self.has_scopes(): parts.append("scopes = %s" % self.get_scopes().shortrepr())
        return "(%s)" % ", ".join(parts)


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
        offset = 0
        p = self._read_fast_ptr(offset)
        if p == _E_IS_FAR_POINTER:
            offset, p = self._read_far_ptr(offset)
        else:
            offset += self._ptrs_offset
        if p == 0:
            return None
        obj = Value.__new__(Value)
        obj._init_from_pointer(self._buf, offset, p)
        return obj
    
    def get_value(self):
        res = self.value
        if res is None:
            return Value.from_buffer('', 0, data_size=0, ptrs_size=0)
        return res
    
    def has_value(self):
        ptr = self._read_fast_ptr(0)
        return ptr != 0
    
    @property
    def brand(self):
        # no union check
        offset = 8
        p = self._read_fast_ptr(offset)
        if p == _E_IS_FAR_POINTER:
            offset, p = self._read_far_ptr(offset)
        else:
            offset += self._ptrs_offset
        if p == 0:
            return None
        obj = Brand.__new__(Brand)
        obj._init_from_pointer(self._buf, offset, p)
        return obj
    
    def get_brand(self):
        res = self.brand
        if res is None:
            return Brand.from_buffer('', 0, data_size=0, ptrs_size=0)
        return res
    
    def has_brand(self):
        ptr = self._read_fast_ptr(8)
        return ptr != 0
    
    @staticmethod
    def __new(id=0, value=None, brand=None):
        builder = _StructBuilder('Qqq')
        value = builder.alloc_struct(8, Value, value)
        brand = builder.alloc_struct(16, Brand, brand)
        buf = builder.build(id, value, brand)
        return buf
    
    def __init__(self, id=0, value=None, brand=None):
        _buf = self.__new(id, value, brand)
        _Struct.__init__(self, _buf, 0, 1, 2)
    
    def shortrepr(self):
        parts = []
        parts.append("id = %s" % self.id)
        if self.has_value(): parts.append("value = %s" % self.get_value().shortrepr())
        if self.has_brand(): parts.append("brand = %s" % self.get_brand().shortrepr())
        return "(%s)" % ", ".join(parts)


@Node_interface.__extend__
class Node_interface(_Struct):
    __static_data_size__ = 5
    __static_ptrs_size__ = 6
    
    
    @property
    def methods(self):
        # no union check
        return self._read_list(24, _StructList, Method)
    
    def get_methods(self):
        res = self.methods
        if res is None:
            return _StructList.from_buffer('', 0, 0, 0, Method)
        return res
    
    def has_methods(self):
        ptr = self._read_fast_ptr(24)
        return ptr != 0
    
    @property
    def superclasses(self):
        # no union check
        return self._read_list(32, _StructList, Superclass)
    
    def get_superclasses(self):
        res = self.superclasses
        if res is None:
            return _StructList.from_buffer('', 0, 0, 0, Superclass)
        return res
    
    def has_superclasses(self):
        ptr = self._read_fast_ptr(32)
        return ptr != 0
    
    def shortrepr(self):
        parts = []
        if self.has_methods(): parts.append("methods = %s" % self.get_methods().shortrepr())
        if self.has_superclasses(): parts.append("superclasses = %s" % self.get_superclasses().shortrepr())
        return "(%s)" % ", ".join(parts)


@Node_const.__extend__
class Node_const(_Struct):
    __static_data_size__ = 5
    __static_ptrs_size__ = 6
    
    
    @property
    def type(self):
        # no union check
        offset = 24
        p = self._read_fast_ptr(offset)
        if p == _E_IS_FAR_POINTER:
            offset, p = self._read_far_ptr(offset)
        else:
            offset += self._ptrs_offset
        if p == 0:
            return None
        obj = Type.__new__(Type)
        obj._init_from_pointer(self._buf, offset, p)
        return obj
    
    def get_type(self):
        res = self.type
        if res is None:
            return Type.from_buffer('', 0, data_size=0, ptrs_size=0)
        return res
    
    def has_type(self):
        ptr = self._read_fast_ptr(24)
        return ptr != 0
    
    @property
    def value(self):
        # no union check
        offset = 32
        p = self._read_fast_ptr(offset)
        if p == _E_IS_FAR_POINTER:
            offset, p = self._read_far_ptr(offset)
        else:
            offset += self._ptrs_offset
        if p == 0:
            return None
        obj = Value.__new__(Value)
        obj._init_from_pointer(self._buf, offset, p)
        return obj
    
    def get_value(self):
        res = self.value
        if res is None:
            return Value.from_buffer('', 0, data_size=0, ptrs_size=0)
        return res
    
    def has_value(self):
        ptr = self._read_fast_ptr(32)
        return ptr != 0
    
    def shortrepr(self):
        parts = []
        if self.has_type(): parts.append("type = %s" % self.get_type().shortrepr())
        if self.has_value(): parts.append("value = %s" % self.get_value().shortrepr())
        return "(%s)" % ", ".join(parts)


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
        value = self._read_enum(26, ElementSize)
        if 0 != 0:
            value = ElementSize(value ^ 0)
        return value
    
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
    
    def get_fields(self):
        res = self.fields
        if res is None:
            return _StructList.from_buffer('', 0, 0, 0, Field)
        return res
    
    def has_fields(self):
        ptr = self._read_fast_ptr(24)
        return ptr != 0
    
    def shortrepr(self):
        parts = []
        parts.append("dataWordCount = %s" % self.dataWordCount)
        parts.append("pointerCount = %s" % self.pointerCount)
        parts.append("preferredListEncoding = %s" % self.preferredListEncoding)
        parts.append("isGroup = %s" % str(self.isGroup).lower())
        parts.append("discriminantCount = %s" % self.discriminantCount)
        parts.append("discriminantOffset = %s" % self.discriminantOffset)
        if self.has_fields(): parts.append("fields = %s" % self.get_fields().shortrepr())
        return "(%s)" % ", ".join(parts)


@Node_annotation.__extend__
class Node_annotation(_Struct):
    __static_data_size__ = 5
    __static_ptrs_size__ = 6
    
    
    @property
    def type(self):
        # no union check
        offset = 24
        p = self._read_fast_ptr(offset)
        if p == _E_IS_FAR_POINTER:
            offset, p = self._read_far_ptr(offset)
        else:
            offset += self._ptrs_offset
        if p == 0:
            return None
        obj = Type.__new__(Type)
        obj._init_from_pointer(self._buf, offset, p)
        return obj
    
    def get_type(self):
        res = self.type
        if res is None:
            return Type.from_buffer('', 0, data_size=0, ptrs_size=0)
        return res
    
    def has_type(self):
        ptr = self._read_fast_ptr(24)
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
    
    def shortrepr(self):
        parts = []
        if self.has_type(): parts.append("type = %s" % self.get_type().shortrepr())
        parts.append("targetsFile = %s" % str(self.targetsFile).lower())
        parts.append("targetsConst = %s" % str(self.targetsConst).lower())
        parts.append("targetsEnum = %s" % str(self.targetsEnum).lower())
        parts.append("targetsEnumerant = %s" % str(self.targetsEnumerant).lower())
        parts.append("targetsStruct = %s" % str(self.targetsStruct).lower())
        parts.append("targetsField = %s" % str(self.targetsField).lower())
        parts.append("targetsUnion = %s" % str(self.targetsUnion).lower())
        parts.append("targetsGroup = %s" % str(self.targetsGroup).lower())
        parts.append("targetsInterface = %s" % str(self.targetsInterface).lower())
        parts.append("targetsMethod = %s" % str(self.targetsMethod).lower())
        parts.append("targetsParam = %s" % str(self.targetsParam).lower())
        parts.append("targetsAnnotation = %s" % str(self.targetsAnnotation).lower())
        return "(%s)" % ", ".join(parts)


@Node_enum.__extend__
class Node_enum(_Struct):
    __static_data_size__ = 5
    __static_ptrs_size__ = 6
    
    
    @property
    def enumerants(self):
        # no union check
        return self._read_list(24, _StructList, Enumerant)
    
    def get_enumerants(self):
        res = self.enumerants
        if res is None:
            return _StructList.from_buffer('', 0, 0, 0, Enumerant)
        return res
    
    def has_enumerants(self):
        ptr = self._read_fast_ptr(24)
        return ptr != 0
    
    def shortrepr(self):
        parts = []
        if self.has_enumerants(): parts.append("enumerants = %s" % self.get_enumerants().shortrepr())
        return "(%s)" % ", ".join(parts)


@Node_NestedNode.__extend__
class Node_NestedNode(_Struct):
    __static_data_size__ = 1
    __static_ptrs_size__ = 1
    
    
    @property
    def name(self):
        # no union check
        return self._read_str_text(0)
    
    def get_name(self):
        return self._read_str_text(0, default_="")
    
    def has_name(self):
        ptr = self._read_fast_ptr(0)
        return ptr != 0
    
    @property
    def id(self):
        # no union check
        value = self._read_data(0, ord('Q'))
        if 0 != 0:
            value = value ^ 0
        return value
    
    @staticmethod
    def __new(name=None, id=0):
        builder = _StructBuilder('Qq')
        name = builder.alloc_text(8, name)
        buf = builder.build(id, name)
        return buf
    
    def __init__(self, name=None, id=0):
        _buf = self.__new(name, id)
        _Struct.__init__(self, _buf, 0, 1, 1)
    
    def shortrepr(self):
        parts = []
        if self.has_name(): parts.append("name = %s" % _text_repr(self.get_name()))
        parts.append("id = %s" % self.id)
        return "(%s)" % ", ".join(parts)


@Node_Parameter.__extend__
class Node_Parameter(_Struct):
    __static_data_size__ = 0
    __static_ptrs_size__ = 1
    
    
    @property
    def name(self):
        # no union check
        return self._read_str_text(0)
    
    def get_name(self):
        return self._read_str_text(0, default_="")
    
    def has_name(self):
        ptr = self._read_fast_ptr(0)
        return ptr != 0
    
    @staticmethod
    def __new(name=None):
        builder = _StructBuilder('q')
        name = builder.alloc_text(0, name)
        buf = builder.build(name)
        return buf
    
    def __init__(self, name=None):
        _buf = self.__new(name)
        _Struct.__init__(self, _buf, 0, 0, 1)
    
    def shortrepr(self):
        parts = []
        if self.has_name(): parts.append("name = %s" % _text_repr(self.get_name()))
        return "(%s)" % ", ".join(parts)


@Node.__extend__
class Node(_Struct):
    __static_data_size__ = 5
    __static_ptrs_size__ = 6
    
    NestedNode = Node_NestedNode
    Parameter = Node_Parameter
    
    __tag_offset__ = 12
    __tag__ = _enum('Node.__tag__', ['file', 'struct', 'enum', 'interface', 'const', 'annotation'])
    
    def is_file(self):
        return self._read_data_int16(12) == 0
    def is_struct(self):
        return self._read_data_int16(12) == 1
    def is_enum(self):
        return self._read_data_int16(12) == 2
    def is_interface(self):
        return self._read_data_int16(12) == 3
    def is_const(self):
        return self._read_data_int16(12) == 4
    def is_annotation(self):
        return self._read_data_int16(12) == 5
    
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
    
    def get_displayName(self):
        return self._read_str_text(0, default_="")
    
    def has_displayName(self):
        ptr = self._read_fast_ptr(0)
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
    
    def get_nestedNodes(self):
        res = self.nestedNodes
        if res is None:
            return _StructList.from_buffer('', 0, 0, 0, Node.NestedNode)
        return res
    
    def has_nestedNodes(self):
        ptr = self._read_fast_ptr(8)
        return ptr != 0
    
    @property
    def annotations(self):
        # no union check
        return self._read_list(16, _StructList, Annotation)
    
    def get_annotations(self):
        res = self.annotations
        if res is None:
            return _StructList.from_buffer('', 0, 0, 0, Annotation)
        return res
    
    def has_annotations(self):
        ptr = self._read_fast_ptr(16)
        return ptr != 0
    
    @property
    def file(self):
        self._ensure_union(0)
        return None
    
    @property
    def struct(self):
        self._ensure_union(1)
        obj = Node_struct.__new__(Node_struct)
        _Struct._init_from_buffer(obj, self._buf, self._data_offset,
                                  self._data_size, self._ptrs_size)
        return obj
    
    @staticmethod
    def Struct(dataWordCount=0, pointerCount=0, preferredListEncoding=0, isGroup=False, discriminantCount=0, discriminantOffset=0, fields=None):
        return dataWordCount, pointerCount, preferredListEncoding, isGroup, discriminantCount, discriminantOffset, fields,
    
    @property
    def enum(self):
        self._ensure_union(2)
        obj = Node_enum.__new__(Node_enum)
        _Struct._init_from_buffer(obj, self._buf, self._data_offset,
                                  self._data_size, self._ptrs_size)
        return obj
    
    @staticmethod
    def Enum(enumerants=None):
        return enumerants,
    
    @property
    def interface(self):
        self._ensure_union(3)
        obj = Node_interface.__new__(Node_interface)
        _Struct._init_from_buffer(obj, self._buf, self._data_offset,
                                  self._data_size, self._ptrs_size)
        return obj
    
    @staticmethod
    def Interface(methods=None, superclasses=None):
        return methods, superclasses,
    
    @property
    def const(self):
        self._ensure_union(4)
        obj = Node_const.__new__(Node_const)
        _Struct._init_from_buffer(obj, self._buf, self._data_offset,
                                  self._data_size, self._ptrs_size)
        return obj
    
    @staticmethod
    def Const(type=None, value=None):
        return type, value,
    
    @property
    def annotation(self):
        self._ensure_union(5)
        obj = Node_annotation.__new__(Node_annotation)
        _Struct._init_from_buffer(obj, self._buf, self._data_offset,
                                  self._data_size, self._ptrs_size)
        return obj
    
    @staticmethod
    def Annotation(type=None, targetsFile=False, targetsConst=False, targetsEnum=False, targetsEnumerant=False, targetsStruct=False, targetsField=False, targetsUnion=False, targetsGroup=False, targetsInterface=False, targetsMethod=False, targetsParam=False, targetsAnnotation=False):
        return type, targetsFile, targetsConst, targetsEnum, targetsEnumerant, targetsStruct, targetsField, targetsUnion, targetsGroup, targetsInterface, targetsMethod, targetsParam, targetsAnnotation,
    
    @property
    def parameters(self):
        # no union check
        return self._read_list(40, _StructList, Node.Parameter)
    
    def get_parameters(self):
        res = self.parameters
        if res is None:
            return _StructList.from_buffer('', 0, 0, 0, Node.Parameter)
        return res
    
    def has_parameters(self):
        ptr = self._read_fast_ptr(40)
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
        raise NotImplementedError('Unsupported field type: (name = "isGeneric", codeOrder = 5, discriminantValue = 65535, slot = (offset = 288, type = (bool = void), defaultValue = (bool = false), hadExplicitDefault = false), ordinal = (explicit = 33))')
    @classmethod
    def new_file(cls):
        buf = cls.__new_file()
        return cls.from_buffer(buf, 0, 5, 6)
    
    @staticmethod
    def __new_struct(*args, **kwargs):
        raise NotImplementedError('Unsupported field type: (name = "isGroup", codeOrder = 3, discriminantValue = 65535, slot = (offset = 224, type = (bool = void), defaultValue = (bool = false), hadExplicitDefault = false), ordinal = (explicit = 10))')
    @classmethod
    def new_struct(cls):
        buf = cls.__new_struct()
        return cls.from_buffer(buf, 0, 5, 6)
    
    @staticmethod
    def __new_enum(*args, **kwargs):
        raise NotImplementedError('Unsupported field type: (name = "isGeneric", codeOrder = 5, discriminantValue = 65535, slot = (offset = 288, type = (bool = void), defaultValue = (bool = false), hadExplicitDefault = false), ordinal = (explicit = 33))')
    @classmethod
    def new_enum(cls):
        buf = cls.__new_enum()
        return cls.from_buffer(buf, 0, 5, 6)
    
    @staticmethod
    def __new_interface(*args, **kwargs):
        raise NotImplementedError('Unsupported field type: (name = "isGeneric", codeOrder = 5, discriminantValue = 65535, slot = (offset = 288, type = (bool = void), defaultValue = (bool = false), hadExplicitDefault = false), ordinal = (explicit = 33))')
    @classmethod
    def new_interface(cls):
        buf = cls.__new_interface()
        return cls.from_buffer(buf, 0, 5, 6)
    
    @staticmethod
    def __new_const(*args, **kwargs):
        raise NotImplementedError('Unsupported field type: (name = "isGeneric", codeOrder = 5, discriminantValue = 65535, slot = (offset = 288, type = (bool = void), defaultValue = (bool = false), hadExplicitDefault = false), ordinal = (explicit = 33))')
    @classmethod
    def new_const(cls):
        buf = cls.__new_const()
        return cls.from_buffer(buf, 0, 5, 6)
    
    @staticmethod
    def __new_annotation(*args, **kwargs):
        raise NotImplementedError('Unsupported field type: (name = "targetsFile", codeOrder = 1, discriminantValue = 65535, slot = (offset = 112, type = (bool = void), defaultValue = (bool = false), hadExplicitDefault = false), ordinal = (explicit = 19))')
    @classmethod
    def new_annotation(cls):
        buf = cls.__new_annotation()
        return cls.from_buffer(buf, 0, 5, 6)
    
    def __init__(self, id=0, displayName=None, displayNamePrefixLength=0, scopeId=0, nestedNodes=None, annotations=None, file=_undefined, struct=(0, 0, 0, False, 0, 0, None,), enum=(None,), interface=(None, None,), const=(None, None,), annotation=(None, False, False, False, False, False, False, False, False, False, False, False, False,), parameters=None, isGeneric=False):
        _buf = None
        _curtag = None
        if file is not _undefined:
            _curtag = _check_tag(_curtag, 'file')
            _buf = self.__new_file()
        if struct is not _undefined:
            _curtag = _check_tag(_curtag, 'struct')
            _buf = self.__new_struct()
        if enum is not _undefined:
            _curtag = _check_tag(_curtag, 'enum')
            _buf = self.__new_enum()
        if interface is not _undefined:
            _curtag = _check_tag(_curtag, 'interface')
            _buf = self.__new_interface()
        if const is not _undefined:
            _curtag = _check_tag(_curtag, 'const')
            _buf = self.__new_const()
        if annotation is not _undefined:
            _curtag = _check_tag(_curtag, 'annotation')
            _buf = self.__new_annotation()
        if _buf is None:
            raise TypeError("one of the following args is required: file, struct, enum, interface, const, annotation")
        _Struct.__init__(self, _buf, 0, 5, 6)
    
    def shortrepr(self):
        parts = []
        parts.append("id = %s" % self.id)
        if self.has_displayName(): parts.append("displayName = %s" % _text_repr(self.get_displayName()))
        parts.append("displayNamePrefixLength = %s" % self.displayNamePrefixLength)
        parts.append("scopeId = %s" % self.scopeId)
        if self.has_nestedNodes(): parts.append("nestedNodes = %s" % self.get_nestedNodes().shortrepr())
        if self.has_annotations(): parts.append("annotations = %s" % self.get_annotations().shortrepr())
        if self.is_file(): parts.append("file = %s" % "void")
        if self.is_struct(): parts.append("struct = %s" % self.struct.shortrepr())
        if self.is_enum(): parts.append("enum = %s" % self.enum.shortrepr())
        if self.is_interface(): parts.append("interface = %s" % self.interface.shortrepr())
        if self.is_const(): parts.append("const = %s" % self.const.shortrepr())
        if self.is_annotation(): parts.append("annotation = %s" % self.annotation.shortrepr())
        if self.has_parameters(): parts.append("parameters = %s" % self.get_parameters().shortrepr())
        parts.append("isGeneric = %s" % str(self.isGeneric).lower())
        return "(%s)" % ", ".join(parts)



del globals()['CodeGeneratorRequest_RequestedFile']
del globals()['CodeGeneratorRequest_RequestedFile_Import']
del globals()['Brand_Binding']
del globals()['Brand_Scope']
del globals()['Node_NestedNode']
del globals()['Node_Parameter']

_extend_module_maybe(globals(), modname=__name__)