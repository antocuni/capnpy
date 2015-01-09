# THIS FILE HAS BEEN GENERATED AUTOMATICALLY BY capnpy
# do not edit by hand
# generated on 2015-01-09 11:26
# input files: 
#   - capnpy/schema.capnp

from capnpy.struct_ import Struct
from capnpy import field
from capnpy.enum import enum
from capnpy.blob import Types
from capnpy.util import extend

class CodeGeneratorRequest(Struct):
    class RequestedFile(Struct):
        class Import(Struct):
            pass
        pass
    pass
class Method(Struct):
    pass
class Enumerant(Struct):
    pass
ElementSize = enum('ElementSize', ('empty', 'bit', 'byte', 'twoBytes', 'fourBytes', 'eightBytes', 'pointer', 'inlineComposite'))
class Type(Struct):
    class anyPointer(Struct):
        class parameter(Struct):
            pass
        class implicitMethodParameter(Struct):
            pass
        pass
    class struct(Struct):
        pass
    class enum(Struct):
        pass
    class interface(Struct):
        pass
    class list(Struct):
        pass
    pass
class Field(Struct):
    class group(Struct):
        pass
    class ordinal(Struct):
        pass
    class slot(Struct):
        pass
    pass
class Superclass(Struct):
    pass
class Value(Struct):
    pass
class Brand(Struct):
    class Binding(Struct):
        pass
    class Scope(Struct):
        pass
    pass
class Annotation(Struct):
    pass
class Node(Struct):
    class interface(Struct):
        pass
    class const(Struct):
        pass
    class struct(Struct):
        pass
    class annotation(Struct):
        pass
    class enum(Struct):
        pass
    class NestedNode(Struct):
        pass
    class Parameter(Struct):
        pass
    pass

@extend(CodeGeneratorRequest)
class _:
    __data_size__ = 0
    __ptrs_size__ = 2
    
    @extend(CodeGeneratorRequest.RequestedFile)
    class _:
        __data_size__ = 1
        __ptrs_size__ = 2
        
        @extend(CodeGeneratorRequest.RequestedFile.Import)
        class _:
            __data_size__ = 1
            __ptrs_size__ = 1
            id = field.Primitive(0, Types.uint64, default=0)
            name = field.String(8)
        id = field.Primitive(0, Types.uint64, default=0)
        filename = field.String(8)
        imports = field.List(16, CodeGeneratorRequest.RequestedFile.Import)
    nodes = field.List(0, Node)
    requestedFiles = field.List(8, CodeGeneratorRequest.RequestedFile)

@extend(Method)
class _:
    __data_size__ = 3
    __ptrs_size__ = 5
    name = field.String(24)
    codeOrder = field.Primitive(0, Types.uint16, default=0)
    paramStructType = field.Primitive(8, Types.uint64, default=0)
    resultStructType = field.Primitive(16, Types.uint64, default=0)
    annotations = field.List(32, Annotation)
    paramBrand = field.Struct(40, Brand)
    resultBrand = field.Struct(48, Brand)
    implicitParameters = field.List(56, Node.Parameter)

@extend(Enumerant)
class _:
    __data_size__ = 1
    __ptrs_size__ = 2
    name = field.String(8)
    codeOrder = field.Primitive(0, Types.uint16, default=0)
    annotations = field.List(16, Annotation)

@extend(Type)
class _:
    __data_size__ = 3
    __ptrs_size__ = 1
    __tag_offset__ = 0
    __tag__ = enum('Type.__tag__', ('void', 'bool', 'int8', 'int16', 'int32', 'int64', 'uint8', 'uint16', 'uint32', 'uint64', 'float32', 'float64', 'text', 'data', 'list', 'enum', 'struct', 'interface', 'anyPointer'))
    void = field.Void()
    void = field.Union(0, void)
    bool = field.Void()
    bool = field.Union(1, bool)
    int8 = field.Void()
    int8 = field.Union(2, int8)
    int16 = field.Void()
    int16 = field.Union(3, int16)
    int32 = field.Void()
    int32 = field.Union(4, int32)
    int64 = field.Void()
    int64 = field.Union(5, int64)
    uint8 = field.Void()
    uint8 = field.Union(6, uint8)
    uint16 = field.Void()
    uint16 = field.Union(7, uint16)
    uint32 = field.Void()
    uint32 = field.Union(8, uint32)
    uint64 = field.Void()
    uint64 = field.Union(9, uint64)
    float32 = field.Void()
    float32 = field.Union(10, float32)
    float64 = field.Void()
    float64 = field.Union(11, float64)
    text = field.Void()
    text = field.Union(12, text)
    data = field.Void()
    data = field.Union(13, data)
    
    @extend(Type.list)
    class _:
        __data_size__ = 3
        __ptrs_size__ = 1
        elementType = field.Struct(24, Type)
    list = field.Group(Type.list)
    list = field.Union(14, list)
    
    @extend(Type.enum)
    class _:
        __data_size__ = 3
        __ptrs_size__ = 1
        typeId = field.Primitive(8, Types.uint64, default=0)
        brand = field.Struct(24, Brand)
    enum = field.Group(Type.enum)
    enum = field.Union(15, enum)
    
    @extend(Type.struct)
    class _:
        __data_size__ = 3
        __ptrs_size__ = 1
        typeId = field.Primitive(8, Types.uint64, default=0)
        brand = field.Struct(24, Brand)
    struct = field.Group(Type.struct)
    struct = field.Union(16, struct)
    
    @extend(Type.interface)
    class _:
        __data_size__ = 3
        __ptrs_size__ = 1
        typeId = field.Primitive(8, Types.uint64, default=0)
        brand = field.Struct(24, Brand)
    interface = field.Group(Type.interface)
    interface = field.Union(17, interface)
    
    @extend(Type.anyPointer)
    class _:
        __data_size__ = 3
        __ptrs_size__ = 1
        __tag_offset__ = 8
        __tag__ = enum('anyPointer.__tag__', ('unconstrained', 'parameter', 'implicitMethodParameter'))
        unconstrained = field.Void()
        unconstrained = field.Union(0, unconstrained)
        
        @extend(Type.anyPointer.parameter)
        class _:
            __data_size__ = 3
            __ptrs_size__ = 1
            scopeId = field.Primitive(16, Types.uint64, default=0)
            parameterIndex = field.Primitive(10, Types.uint16, default=0)
        parameter = field.Group(Type.anyPointer.parameter)
        parameter = field.Union(1, parameter)
        
        @extend(Type.anyPointer.implicitMethodParameter)
        class _:
            __data_size__ = 3
            __ptrs_size__ = 1
            parameterIndex = field.Primitive(10, Types.uint16, default=0)
        implicitMethodParameter = field.Group(Type.anyPointer.implicitMethodParameter)
        implicitMethodParameter = field.Union(2, implicitMethodParameter)
    anyPointer = field.Group(Type.anyPointer)
    anyPointer = field.Union(18, anyPointer)

@extend(Field)
class _:
    __data_size__ = 3
    __ptrs_size__ = 4
    noDiscriminant = 65535
    __tag_offset__ = 8
    __tag__ = enum('Field.__tag__', ('slot', 'group'))
    name = field.String(24)
    codeOrder = field.Primitive(0, Types.uint16, default=0)
    annotations = field.List(32, Annotation)
    discriminantValue = field.Primitive(2, Types.uint16, default=65535)
    
    @extend(Field.slot)
    class _:
        __data_size__ = 3
        __ptrs_size__ = 4
        offset = field.Primitive(4, Types.uint32, default=0)
        type = field.Struct(40, Type)
        defaultValue = field.Struct(48, Value)
        hadExplicitDefault = field.Bool(16, 0, default=False)
    slot = field.Group(Field.slot)
    slot = field.Union(0, slot)
    
    @extend(Field.group)
    class _:
        __data_size__ = 3
        __ptrs_size__ = 4
        typeId = field.Primitive(16, Types.uint64, default=0)
    group = field.Group(Field.group)
    group = field.Union(1, group)
    
    @extend(Field.ordinal)
    class _:
        __data_size__ = 3
        __ptrs_size__ = 4
        __tag_offset__ = 10
        __tag__ = enum('ordinal.__tag__', ('implicit', 'explicit'))
        implicit = field.Void()
        implicit = field.Union(0, implicit)
        explicit = field.Primitive(12, Types.uint16, default=0)
        explicit = field.Union(1, explicit)
    ordinal = field.Group(Field.ordinal)

@extend(Superclass)
class _:
    __data_size__ = 1
    __ptrs_size__ = 1
    id = field.Primitive(0, Types.uint64, default=0)
    brand = field.Struct(8, Brand)

@extend(Value)
class _:
    __data_size__ = 2
    __ptrs_size__ = 1
    __tag_offset__ = 0
    __tag__ = enum('Value.__tag__', ('void', 'bool', 'int8', 'int16', 'int32', 'int64', 'uint8', 'uint16', 'uint32', 'uint64', 'float32', 'float64', 'text', 'data', 'list', 'enum', 'struct', 'interface', 'anyPointer'))
    void = field.Void()
    void = field.Union(0, void)
    bool = field.Bool(2, 0, default=False)
    bool = field.Union(1, bool)
    int8 = field.Primitive(2, Types.int8, default=0)
    int8 = field.Union(2, int8)
    int16 = field.Primitive(2, Types.int16, default=0)
    int16 = field.Union(3, int16)
    int32 = field.Primitive(4, Types.int32, default=0)
    int32 = field.Union(4, int32)
    int64 = field.Primitive(8, Types.int64, default=0)
    int64 = field.Union(5, int64)
    uint8 = field.Primitive(2, Types.uint8, default=0)
    uint8 = field.Union(6, uint8)
    uint16 = field.Primitive(2, Types.uint16, default=0)
    uint16 = field.Union(7, uint16)
    uint32 = field.Primitive(4, Types.uint32, default=0)
    uint32 = field.Union(8, uint32)
    uint64 = field.Primitive(8, Types.uint64, default=0)
    uint64 = field.Union(9, uint64)
    float32 = field.Primitive(4, Types.float32, default=0.0)
    float32 = field.Union(10, float32)
    float64 = field.Primitive(8, Types.float64, default=0.0)
    float64 = field.Union(11, float64)
    text = field.String(16)
    text = field.Union(12, text)
    data = field.Data(16)
    data = field.Union(13, data)
    list = field.AnyPointer(16)
    list = field.Union(14, list)
    enum = field.Primitive(2, Types.uint16, default=0)
    enum = field.Union(15, enum)
    struct = field.AnyPointer(16)
    struct = field.Union(16, struct)
    interface = field.Void()
    interface = field.Union(17, interface)
    anyPointer = field.AnyPointer(16)
    anyPointer = field.Union(18, anyPointer)

@extend(Brand)
class _:
    __data_size__ = 0
    __ptrs_size__ = 1
    
    @extend(Brand.Binding)
    class _:
        __data_size__ = 1
        __ptrs_size__ = 1
        __tag_offset__ = 0
        __tag__ = enum('Binding.__tag__', ('unbound', 'type'))
        unbound = field.Void()
        unbound = field.Union(0, unbound)
        type = field.Struct(8, Type)
        type = field.Union(1, type)
    
    @extend(Brand.Scope)
    class _:
        __data_size__ = 2
        __ptrs_size__ = 1
        __tag_offset__ = 8
        __tag__ = enum('Scope.__tag__', ('bind', 'inherit'))
        scopeId = field.Primitive(0, Types.uint64, default=0)
        bind = field.List(16, Brand.Binding)
        bind = field.Union(0, bind)
        inherit = field.Void()
        inherit = field.Union(1, inherit)
    scopes = field.List(0, Brand.Scope)

@extend(Annotation)
class _:
    __data_size__ = 1
    __ptrs_size__ = 2
    id = field.Primitive(0, Types.uint64, default=0)
    value = field.Struct(8, Value)
    brand = field.Struct(16, Brand)

@extend(Node)
class _:
    __data_size__ = 5
    __ptrs_size__ = 6
    
    @extend(Node.NestedNode)
    class _:
        __data_size__ = 1
        __ptrs_size__ = 1
        name = field.String(8)
        id = field.Primitive(0, Types.uint64, default=0)
    
    @extend(Node.Parameter)
    class _:
        __data_size__ = 0
        __ptrs_size__ = 1
        name = field.String(0)
    __tag_offset__ = 12
    __tag__ = enum('Node.__tag__', ('file', 'struct', 'enum', 'interface', 'const', 'annotation'))
    id = field.Primitive(0, Types.uint64, default=0)
    displayName = field.String(40)
    displayNamePrefixLength = field.Primitive(8, Types.uint32, default=0)
    scopeId = field.Primitive(16, Types.uint64, default=0)
    nestedNodes = field.List(48, Node.NestedNode)
    annotations = field.List(56, Annotation)
    file = field.Void()
    file = field.Union(0, file)
    
    @extend(Node.struct)
    class _:
        __data_size__ = 5
        __ptrs_size__ = 6
        dataWordCount = field.Primitive(14, Types.uint16, default=0)
        pointerCount = field.Primitive(24, Types.uint16, default=0)
        preferredListEncoding = field.Enum(26, ElementSize)
        isGroup = field.Bool(28, 0, default=False)
        discriminantCount = field.Primitive(30, Types.uint16, default=0)
        discriminantOffset = field.Primitive(32, Types.uint32, default=0)
        fields = field.List(64, Field)
    struct = field.Group(Node.struct)
    struct = field.Union(1, struct)
    
    @extend(Node.enum)
    class _:
        __data_size__ = 5
        __ptrs_size__ = 6
        enumerants = field.List(64, Enumerant)
    enum = field.Group(Node.enum)
    enum = field.Union(2, enum)
    
    @extend(Node.interface)
    class _:
        __data_size__ = 5
        __ptrs_size__ = 6
        methods = field.List(64, Method)
        superclasses = field.List(72, Superclass)
    interface = field.Group(Node.interface)
    interface = field.Union(3, interface)
    
    @extend(Node.const)
    class _:
        __data_size__ = 5
        __ptrs_size__ = 6
        type = field.Struct(64, Type)
        value = field.Struct(72, Value)
    const = field.Group(Node.const)
    const = field.Union(4, const)
    
    @extend(Node.annotation)
    class _:
        __data_size__ = 5
        __ptrs_size__ = 6
        type = field.Struct(64, Type)
        targetsFile = field.Bool(14, 0, default=False)
        targetsConst = field.Bool(14, 1, default=False)
        targetsEnum = field.Bool(14, 2, default=False)
        targetsEnumerant = field.Bool(14, 3, default=False)
        targetsStruct = field.Bool(14, 4, default=False)
        targetsField = field.Bool(14, 5, default=False)
        targetsUnion = field.Bool(14, 6, default=False)
        targetsGroup = field.Bool(14, 7, default=False)
        targetsInterface = field.Bool(15, 0, default=False)
        targetsMethod = field.Bool(15, 1, default=False)
        targetsParam = field.Bool(15, 2, default=False)
        targetsAnnotation = field.Bool(15, 3, default=False)
    annotation = field.Group(Node.annotation)
    annotation = field.Union(5, annotation)
    parameters = field.List(80, Node.Parameter)
    isGeneric = field.Bool(36, 0, default=False)
