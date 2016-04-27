# This is the cython version of ptr.py: all the logic is implemented as C
# macros in ptr.h.
#
# In theory, Cython should be able to produce the Python-side wrappers of all
# the constants and macros declared in ptr.h/ptr.pxd: however, it does not
# seem to handle well the fact that we give different names in Python and C
# (e.g. ptr.kind vs PTR_KIND), so we need to do some wrap by hand, playing
# with globals() to avoid syntax errors.

globals()['STRUCT'] = STRUCT
globals()['LIST'] = LIST
globals()['FAR'] = FAR
globals()['LIST_SIZE_BIT'] = LIST_SIZE_BIT
globals()['LIST_SIZE_8'] = LIST_SIZE_8
globals()['LIST_SIZE_16'] = LIST_SIZE_16
globals()['LIST_SIZE_32'] = LIST_SIZE_32
globals()['LIST_SIZE_64'] = LIST_SIZE_64
globals()['LIST_SIZE_PTR'] = LIST_SIZE_PTR
globals()['LIST_SIZE_COMPOSITE'] = LIST_SIZE_COMPOSITE
globals()['E_IS_FAR_POINTER'] = E_IS_FAR_POINTER
LIST_SIZE_LENGTH = (None, None, 1, 2, 4, 8, 8)

def remove_underscore(func):
    name = func.__name__
    assert name.startswith('_')
    name = name[1:]
    globals()[name] = func
    return None

@remove_underscore
def _kind(ptr): return kind(ptr)

@remove_underscore
def _new_generic(kind, offset, extra):
    return new_generic(kind, offset, extra)

@remove_underscore
def _kind(ptr):
    return kind(ptr)
    
@remove_underscore
def _offset(ptr):
    return offset(ptr)

@remove_underscore
def _extra(ptr):
    return extra(ptr)
    
@remove_underscore
def _deref(ptr, ofs):
    return deref(ptr, ofs)

@remove_underscore
def _new_struct(offset, data_size, ptrs_size):
    return new_struct(offset, data_size, ptrs_size)
    
@remove_underscore
def _struct_data_size(ptr):
    return struct_data_size(ptr)

@remove_underscore
def _struct_ptrs_size(ptr):
    return struct_ptrs_size(ptr)

@remove_underscore
def _new_list(ptr_offset, size_tag, item_count):
    return new_list(ptr_offset, size_tag, item_count)

@remove_underscore
def _list_size_tag(ptr):
    return list_size_tag(ptr)
    
@remove_underscore
def _list_item_count(ptr):
    return list_item_count(ptr)

@remove_underscore
def _new_far(landing_pad, offset, target):
    return new_far(landing_pad, offset, target)
    
@remove_underscore
def _far_landing_pad(ptr):
    return far_landing_pad(ptr)

@remove_underscore
def _far_offset(ptr):
    return far_offset(ptr)
    
@remove_underscore
def _far_target(ptr):
    return far_target(ptr)

