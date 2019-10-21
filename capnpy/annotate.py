# THIS FILE HAS BEEN GENERATED AUTOMATICALLY BY capnpy
# do not edit by hand
# generated on 2019-10-21 11:28
# cython: language_level=2

from capnpy import ptr as _ptr
from capnpy.struct_ import Struct as _Struct
from capnpy.struct_ import check_tag as _check_tag
from capnpy.struct_ import undefined as _undefined
from capnpy.enum import enum as _enum, fill_enum as _fill_enum
from capnpy.enum import BaseEnum as _BaseEnum
from capnpy.type import Types as _Types
from capnpy.segment.builder import SegmentBuilder as _SegmentBuilder
from capnpy.list import List as _List
from capnpy.list import PrimitiveItemType as _PrimitiveItemType
from capnpy.list import BoolItemType as _BoolItemType
from capnpy.list import TextItemType as _TextItemType
from capnpy.list import TextUnicodeItemType as _TextUnicodeItemType
from capnpy.list import StructItemType as _StructItemType
from capnpy.list import EnumItemType as _EnumItemType
from capnpy.list import VoidItemType as _VoidItemType
from capnpy.list import ListItemType as _ListItemType
from capnpy.anypointer import AnyPointer as _AnyPointer
from capnpy.util import text_bytes_repr as _text_bytes_repr
from capnpy.util import text_unicode_repr as _text_unicode_repr
from capnpy.util import float32_repr as _float32_repr
from capnpy.util import float64_repr as _float64_repr
from capnpy.util import extend_module_maybe as _extend_module_maybe
from capnpy.util import check_version as _check_version
from capnpy.util import encode_maybe as _encode_maybe
__capnpy_id__ = 0xbc24c21845631520
__capnpy_version__ = '0.7.1.dev8+g4a9c343'
__capnproto_version__ = '0.7.0'
# schema compiled with --no-version-check, skipping the call to _check_version
# not including reflection data

#### FORWARD DECLARATIONS ####

class key(object):
    __capnpy_id__ = 0xcb6c062c1b3cf586
    targets_file = False
    targets_const = False
    targets_enum = False
    targets_enumerant = False
    targets_struct = True
    targets_field = True
    targets_union = False
    targets_group = True
    targets_interface = False
    targets_method = False
    targets_param = False
    targets_annotation = False
class nullable(object):
    __capnpy_id__ = 0x9cc3dea2b1b5e7dd
    targets_file = False
    targets_const = False
    targets_enum = False
    targets_enumerant = False
    targets_struct = False
    targets_field = False
    targets_union = False
    targets_group = True
    targets_interface = False
    targets_method = False
    targets_param = False
    targets_annotation = False
class group(object):
    __capnpy_id__ = 0xb02c044a1e63b88d
    targets_file = False
    targets_const = False
    targets_enum = False
    targets_enumerant = False
    targets_struct = False
    targets_field = True
    targets_union = False
    targets_group = False
    targets_interface = False
    targets_method = False
    targets_param = False
    targets_annotation = False
class BoolOption(_BaseEnum):
    __capnpy_id__ = 16217900014262541116
    __members__ = ('false', 'true', 'notset',)
    @staticmethod
    def _new(x):
        return BoolOption(x)
_fill_enum(BoolOption)
_BoolOption_list_item_type = _EnumItemType(BoolOption)

class TextType(_BaseEnum):
    __capnpy_id__ = 15347717153063870105
    __members__ = ('notset', 'bytes', 'unicode',)
    @staticmethod
    def _new(x):
        return TextType(x)
_fill_enum(TextType)
_TextType_list_item_type = _EnumItemType(TextType)

class Options(_Struct): pass
Options.__name__ = 'Options'

class options(object):
    __capnpy_id__ = 0xbdb63a67441ed493
    targets_file = True
    targets_const = False
    targets_enum = False
    targets_enumerant = False
    targets_struct = True
    targets_field = True
    targets_union = False
    targets_group = False
    targets_interface = False
    targets_method = False
    targets_param = False
    targets_annotation = False

#### DEFINITIONS ####

@Options.__extend__
class Options(_Struct):
    __capnpy_id__ = 0xd393b3843dc6b5f3
    __static_data_size__ = 1
    __static_ptrs_size__ = 0
    
    
    @property
    def version_check(self):
        # no union check
        value = self._read_int16(0)
        if 2 != 0:
            value = (value ^ 2)
        return BoolOption._new(value)
    
    @property
    def convert_case(self):
        # no union check
        value = self._read_int16(2)
        if 2 != 0:
            value = (value ^ 2)
        return BoolOption._new(value)
    
    @property
    def text_type(self):
        # no union check
        value = self._read_int16(4)
        if 0 != 0:
            value = (value ^ 0)
        return TextType._new(value)
    
    @property
    def include_reflection_data(self):
        # no union check
        value = self._read_int16(6)
        if 2 != 0:
            value = (value ^ 2)
        return BoolOption._new(value)
    
    @staticmethod
    def __new(version_check=2, convert_case=2, text_type=0, include_reflection_data=2):
        builder = _SegmentBuilder()
        pos = builder.allocate(8)
        version_check ^= 2
        builder.write_int16(pos + 0, version_check)
        convert_case ^= 2
        builder.write_int16(pos + 2, convert_case)
        text_type ^= 0
        builder.write_int16(pos + 4, text_type)
        include_reflection_data ^= 2
        builder.write_int16(pos + 6, include_reflection_data)
        return builder.as_string()
    
    def __init__(self, version_check=2, convert_case=2, text_type=0, include_reflection_data=2):
        _buf = Options.__new(version_check, convert_case, text_type, include_reflection_data)
        self._init_from_buffer(_buf, 0, 1, 0)
    
    def shortrepr(self):
        parts = []
        parts.append("versionCheck = %s" % self.version_check)
        parts.append("convertCase = %s" % self.convert_case)
        parts.append("textType = %s" % self.text_type)
        parts.append("includeReflectionData = %s" % self.include_reflection_data)
        return "(%s)" % ", ".join(parts)

_Options_list_item_type = _StructItemType(Options)


_extend_module_maybe(globals(), modname=__name__)