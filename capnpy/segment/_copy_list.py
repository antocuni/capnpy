def copy_from_list(dst, pos, item_type, lst):
    item_length, size_tag = item_type.get_item_length()
    item_count = len(lst)
    body_length = item_length * item_count
    pos = dst.alloc_list(pos, size_tag, item_count, body_length)
    for item in lst:
        dst.write_int64(pos, item) # XXX
        pos += item_length
