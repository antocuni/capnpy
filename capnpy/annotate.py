# THIS FILE HAS BEEN GENERATED AUTOMATICALLY BY capnpy
# do not edit by hand
# generated on 2017-05-31 12:17

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
from capnpy.list import StructItemType as _StructItemType
from capnpy.list import EnumItemType as _EnumItemType
from capnpy.list import VoidItemType as _VoidItemType
from capnpy.list import ListItemType as _ListItemType
from capnpy.util import text_repr as _text_repr
from capnpy.util import float32_repr as _float32_repr
from capnpy.util import float64_repr as _float64_repr
from capnpy.util import extend_module_maybe as _extend_module_maybe

#### FORWARD DECLARATIONS ####

class key(object):
    __id__ = 14658097673689429382
    targets_file = False
    targets_const = False
    targets_enum = False
    targets_enumerant = False
    targets_struct = True
    targets_field = False
    targets_union = False
    targets_group = True
    targets_interface = False
    targets_method = False
    targets_param = False
    targets_annotation = False
class Options_pyx(_Struct): pass
Options_pyx.__name__ = 'Options.pyx'

class Options_convertCase(_Struct): pass
Options_convertCase.__name__ = 'Options.convertCase'

class Options(_Struct): pass
Options.__name__ = 'Options'

class nullable(object):
    __id__ = 11296117080722892765
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

#### DEFINITIONS ####

@Options_pyx.__extend__
class Options_pyx(_Struct):
    __static_data_size__ = 1
    __static_ptrs_size__ = 0
    
    
    @property
    def is_null(self):
        # no union check
        value = self._read_bit(0, 1)
        if True != 0:
            value = value ^ True
        return value
    
    @property
    def value(self):
        # no union check
        value = self._read_bit(0, 2)
        if False != 0:
            value = value ^ False
        return value
    
    def shortrepr(self):
        parts = []
        parts.append("is_null = %s" % str(self.is_null).lower())
        parts.append("value = %s" % str(self.value).lower())
        return "(%s)" % ", ".join(parts)

_Options_pyx_list_item_type = _StructItemType(Options_pyx)

@Options_convertCase.__extend__
class Options_convertCase(_Struct):
    __static_data_size__ = 1
    __static_ptrs_size__ = 0
    
    
    @property
    def is_null(self):
        # no union check
        value = self._read_bit(0, 4)
        if True != 0:
            value = value ^ True
        return value
    
    @property
    def value(self):
        # no union check
        value = self._read_bit(0, 8)
        if False != 0:
            value = value ^ False
        return value
    
    def shortrepr(self):
        parts = []
        parts.append("is_null = %s" % str(self.is_null).lower())
        parts.append("value = %s" % str(self.value).lower())
        return "(%s)" % ", ".join(parts)

_Options_convertCase_list_item_type = _StructItemType(Options_convertCase)

@Options.__extend__
class Options(_Struct):
    __static_data_size__ = 1
    __static_ptrs_size__ = 0
    
    
    @property
    def pyx(self):
        g = self._pyx
        if g.is_null:
            return None
        return g.value
    
    @property
    def _pyx(self):
        # no union check
        obj = Options_pyx.__new__(Options_pyx)
        _Struct._init_from_buffer(obj, self._seg, self._data_offset,
                                  self._data_size, self._ptrs_size)
        return obj
    
    @property
    def convert_case(self):
        g = self._convert_case
        if g.is_null:
            return None
        return g.value
    
    @property
    def _convert_case(self):
        # no union check
        obj = Options_convertCase.__new__(Options_convertCase)
        _Struct._init_from_buffer(obj, self._seg, self._data_offset,
                                  self._data_size, self._ptrs_size)
        return obj
    
    @staticmethod
    def __new(pyx=None, convert_case=None):
        builder = _SegmentBuilder()
        pos = builder.allocate(8)
        if pyx is None:
            pyx_is_null = 1
            pyx_value = 0
        else:
            pyx_is_null = 0
            pyx_value = pyx
        pyx_is_null ^= True
        builder.write_bool(0, 0, pyx_is_null)
        builder.write_bool(0, 1, pyx_value)
        if convert_case is None:
            convert_case_is_null = 1
            convert_case_value = 0
        else:
            convert_case_is_null = 0
            convert_case_value = convert_case
        convert_case_is_null ^= True
        builder.write_bool(0, 2, convert_case_is_null)
        builder.write_bool(0, 3, convert_case_value)
        return builder.as_string()
    
    def __init__(self, pyx=None, convert_case=None):
        _buf = Options.__new(pyx, convert_case)
        self._init_from_buffer(_buf, 0, 1, 0)
    
    def shortrepr(self):
        parts = []
        parts.append("pyx = %s" % self.pyx.shortrepr())
        parts.append("convert_case = %s" % self.convert_case.shortrepr())
        return "(%s)" % ", ".join(parts)

_Options_list_item_type = _StructItemType(Options)


_extend_module_maybe(globals(), modname=__name__)