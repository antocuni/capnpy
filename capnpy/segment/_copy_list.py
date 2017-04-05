def copy_from_list(builder, pos, item_type, lst):
    item_length, size_tag = item_type.get_item_length()
    item_count = len(lst)
    body_length = item_length * item_count
    pos = builder.alloc_list(pos, size_tag, item_count, body_length)
    for item in lst:
        item_type.write_item(builder, pos, item)
        pos += item_length
