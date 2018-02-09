from capnpy import ptr

def endof(seg, p, offset):
    """
    Check whether the given object is compact, and in that case compute its
    end boundary. If it's not compact, return -1.

    An object is compact if:

      1. there is no gap between its data section and its ptrs section

      2. there is no gap between children

      3. its children are compact

      4. there are no FAR pointers
    """
    kind = ptr.kind(p)
    offset = ptr.deref(p, offset)
    if kind == ptr.STRUCT:
        data_size = ptr.struct_data_size(p)
        ptrs_size = ptr.struct_ptrs_size(p)
        return _endof_struct(seg, p, offset, data_size, ptrs_size)
    elif kind == ptr.LIST:
        item_size = ptr.list_size_tag(p)
        count = ptr.list_item_count(p)
        if item_size == ptr.LIST_SIZE_COMPOSITE:
            tag = seg.read_ptr(offset)
            count = ptr.offset(tag)
            data_size = ptr.struct_data_size(tag)
            ptrs_size = ptr.struct_ptrs_size(tag)
            return _endof_list_composite(seg, p, offset,
                                         count, data_size, ptrs_size)
        elif item_size == ptr.LIST_SIZE_PTR:
            return _endof_list_ptr(seg, p, offset, count)
        elif item_size == ptr.LIST_SIZE_BIT:
            return _endof_list_bit(seg, p, offset, count)
        else:
            return _endof_list_primitive(seg, p, offset, item_size, count)
    elif kind == ptr.FAR:
        return -1
    else:
        assert False, 'unknown ptr kind'

def _endof_ptrs(seg, offset, ptrs_size, current_end):
    i = 0
    while i < ptrs_size:
        p_offset = offset + i*8
        i += 1
        p = seg.read_ptr(p_offset)
        if not p:
            continue
        new_start = ptr.deref(p, p_offset)
        if new_start != current_end:
            return -1
        current_end = endof(seg, p, p_offset)
    #
    return current_end

def _endof_struct(seg, p, offset, data_size, ptrs_size):
    offset += data_size*8
    current_end = offset + (ptrs_size*8)
    return _endof_ptrs(seg, offset, ptrs_size, current_end)

def _endof_list_composite(seg, p, offset, count, data_size, ptrs_size):
    item_size = (data_size+ptrs_size)*8
    offset += 8 # skip the tag
    end = offset + (item_size)*count
    if ptrs_size == 0:
        return end
    #
    i = 0
    while i < count:
        item_offset = offset + (item_size)*i + (data_size*8)
        end = _endof_ptrs(seg, item_offset, ptrs_size, end)
        if end == -1:
            return -1
        i += 1
    #
    return end

def _endof_list_ptr(seg, p, offset, count):
    end = offset + 8*count
    return _endof_ptrs(seg, offset, count, end)

def _endof_list_primitive(seg, p, offset, item_size, count):
    item_size = ptr.list_item_length(item_size)
    return ptr.round_up_to_word(offset + item_size*count)

def _endof_list_bit(seg, p, offset, count):
    bytes_length = ptr.round_up_to_word(count) // 8
    return ptr.round_up_to_word(offset + bytes_length)
