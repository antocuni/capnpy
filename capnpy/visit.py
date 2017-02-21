from capnpy import ptr

def end_of(buf, p, offset):
    """
    Find the end boundary of the object pointed by p.
    This assumes that the buffer is in pre-order.
    """
    kind = ptr.kind(p)
    if kind == ptr.STRUCT:
        return end_of_struct(buf, p, offset)
    elif kind == ptr.LIST:
        item_size = ptr.list_size_tag(p)
        if item_size == ptr.LIST_SIZE_COMPOSITE:
            return end_of_list_composite(buf, p, offset)
        elif item_size == ptr.LIST_SIZE_PTR:
            return end_of_list_ptr(buf, p, offset)
        elif item_size == ptr.LIST_SIZE_BIT:
            return end_of_list_bit(buf, p, offset)
        else:
            return end_of_list_primitive(buf, p, offset)
    elif kind == ptr.FAR:
        raise NotImplementedError('Far pointer not supported')
    else:
        assert False, 'unknown ptr kind'

def end_of_struct(buf, p, offset):
    offset = ptr.deref(p, offset)
    data_size = ptr.struct_data_size(p)
    ptrs_size = ptr.struct_ptrs_size(p)
    offset += data_size*8
    end = end_of_ptrs(buf, offset, ptrs_size)
    if end != -1:
        return end
    return offset + (ptrs_size*8)

def end_of_ptrs(buf, offset, ptrs_size):
    i = ptrs_size
    while i > 0:
        i -= 1
        p2_offset = offset + i*8
        p2 = buf.read_raw_ptr(p2_offset)
        if p2:
            return end_of(buf, p2, p2_offset)
    return -1

def end_of_list_composite(buf, p, offset):
    offset = ptr.deref(p, offset)
    tag = buf.read_raw_ptr(offset)
    offset += 8
    count = ptr.offset(tag)
    data_size = ptr.struct_data_size(tag)
    ptrs_size = ptr.struct_ptrs_size(tag)
    item_size = (data_size+ptrs_size)*8
    if ptrs_size:
        i = count
        while i > 0:
            i -= 1
            item_offset = offset + (item_size)*i + (data_size*8)
            end = end_of_ptrs(buf, item_offset, ptrs_size)
            if end != -1:
                return end
    # no ptr found
    return offset + (item_size)*count

def end_of_list_ptr(buf, p, offset):
    offset = ptr.deref(p, offset)
    count = ptr.list_item_count(p)
    end = end_of_ptrs(buf, offset, count)
    if end != -1:
        return end
    return offset + 8*count

def end_of_list_primitive(buf, p, offset):
    offset = ptr.deref(p, offset)
    count = ptr.list_item_count(p)
    item_size = ptr.list_size_tag(p)
    if item_size == ptr.LIST_SIZE_8:
        item_size = 1
    elif item_size == ptr.LIST_SIZE_16:
        item_size = 2
    elif item_size == ptr.LIST_SIZE_32:
        item_size = 4
    elif item_size == ptr.LIST_SIZE_64:
        item_size = 8
    else:
        assert False, 'Unknown item_size: %s' % item_size
    return offset + item_size*count

def end_of_list_bit(buf, p, offset):
    offset = ptr.deref(p, offset)
    count = ptr.list_item_count(p)
    bytes_length, extra_bits = divmod(count, 8)
    if extra_bits:
        bytes_length += 1
    return offset + bytes_length


def is_compact(buf, p, offset):
    kind = ptr.kind(p)
    if kind == ptr.STRUCT:
        return is_compact_struct(buf, p, offset)
    elif kind == ptr.LIST:
        item_size = ptr.list_size_tag(p)
        if item_size == ptr.LIST_SIZE_COMPOSITE:
            return end_of_list_composite(buf, p, offset)
        elif item_size == ptr.LIST_SIZE_PTR:
            return end_of_list_ptr(buf, p, offset)
        else:
            # primitive or bool
            return True
    elif kind == ptr.FAR:
        raise NotImplementedError('Far pointer not supported')
    else:
        assert False, 'unknown ptr kind'


def is_compact_struct(buf, p, offset):
    """
    A struct is compact if its first non-null pointer points immediately after
    the end of its body.
    """
    offset = ptr.deref(p, offset)
    data_size = ptr.struct_data_size(p)
    ptrs_size = ptr.struct_ptrs_size(p)
    end_of_body = offset + (data_size+ptrs_size)*8
    offset += data_size*8
    i = 0
    while i < ptrs_size:
        p2_offset = offset + i*8
        p2 = buf.read_raw_ptr(p2_offset)
        if p2:
            return ptr.deref(p2, p2_offset) == end_of_body
        i += 1
    return True
