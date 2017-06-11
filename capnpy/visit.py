from capnpy import ptr

class Visitor(object):
    """
    Generic logic for visiting an arbitrary capnp object.
    """

    def visit(self, buf, p, offset):
        kind = ptr.kind(p)
        offset = ptr.deref(p, offset)
        if kind == ptr.STRUCT:
            data_size = ptr.struct_data_size(p)
            ptrs_size = ptr.struct_ptrs_size(p)
            return self.visit_struct(buf, p, offset, data_size, ptrs_size)
        elif kind == ptr.LIST:
            item_size = ptr.list_size_tag(p)
            count = ptr.list_item_count(p)
            if item_size == ptr.LIST_SIZE_COMPOSITE:
                tag = buf.read_ptr(offset)
                count = ptr.offset(tag)
                data_size = ptr.struct_data_size(tag)
                ptrs_size = ptr.struct_ptrs_size(tag)
                return self.visit_list_composite(buf, p, offset,
                                                  count, data_size, ptrs_size)
            elif item_size == ptr.LIST_SIZE_PTR:
                return self.visit_list_ptr(buf, p, offset, count)
            elif item_size == ptr.LIST_SIZE_BIT:
                return self.visit_list_bit(buf, p, offset, count)
            else:
                return self.visit_list_primitive(buf, p, offset, item_size, count)
        elif kind == ptr.FAR:
            raise NotImplementedError('Far pointer not supported')
        else:
            assert False, 'unknown ptr kind'

    def visit_struct(self, buf, p, offset, data_size, ptrs_size):
        raise NotImplementedError

    def visit_list_composite(self, buf, p, offset, count, data_size, ptrs_size):
        raise NotImplementedError

    def visit_list_ptr(self, buf, p, offset, count):
        raise NotImplementedError

    def visit_list_primitive(self, buf, p, offset, item_size, count):
        raise NotImplementedError

    def visit_list_bit(self, buf, p, offset, count):
        raise NotImplementedError

class NotCompact(Exception):
    pass

class EndOf(Visitor):
    """
    Check whether the given object is compact, and in that case compute its
    end boundary. If it's not compact, return -1.

    An object is compact if:

      1. there is no gap between its data section and its ptrs section

      2. there is no gap between children

      3. its children are compact
    """

    def visit_ptrs(self, buf, offset, ptrs_size, current_end):
        i = 0
        while i < ptrs_size:
            p_offset = offset + i*8
            i += 1
            p = buf.read_ptr(p_offset)
            if not p:
                continue
            new_start = ptr.deref(p, p_offset)
            if new_start != current_end:
                raise NotCompact
            current_end = self.visit(buf, p, p_offset)
        #
        return current_end

    def visit_struct(self, buf, p, offset, data_size, ptrs_size):
        offset += data_size*8
        current_end = offset + (ptrs_size*8)
        return self.visit_ptrs(buf, offset, ptrs_size, current_end)

    def visit_list_composite(self, buf, p, offset, count, data_size, ptrs_size):
        item_size = (data_size+ptrs_size)*8
        offset += 8 # skip the tag
        end = offset + (item_size)*count
        if ptrs_size == 0:
            return end
        #
        i = 0
        while i < count:
            item_offset = offset + (item_size)*i + (data_size*8)
            end = self.visit_ptrs(buf, item_offset, ptrs_size, end)
            i += 1
        #
        return end

    def visit_list_ptr(self, buf, p, offset, count):
        end = offset + 8*count
        return self.visit_ptrs(buf, offset, count, end)

    def visit_list_primitive(self, buf, p, offset, item_size, count):
        item_size = ptr.list_item_length(item_size)
        return ptr.round_up_to_word(offset + item_size*count)

    def visit_list_bit(self, buf, p, offset, count):
        bytes_length = ptr.round_up_to_word(count) / 8
        return ptr.round_up_to_word(offset + bytes_length)



def end_of(buf, p, offset):
    try:
        return _end_of.visit(buf, p, offset)
    except NotCompact:
        return -1


_end_of = EndOf()
