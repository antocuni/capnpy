from capnpy.blob import Blob

class List(Blob):

    def __init__(self, buf, offset, item_size, item_count, itemcls):
        """
        buf, offset: the underlying buffer and the offset where the list starts

        item_size: the size of each list item, in BYTES. Note: this is NOT the
        value of the LIST_* tag, although it's obviously based on it

        itemcls: the class of each item, only for list of structs
        """
        Blob.__init__(self, buf, offset)
        self._item_size = item_size
        self._item_count = item_count
        self._itemcls = itemcls

    def _read_list_item(self, offset):
        raise NotImplementedError

    def __len__(self):
        return self._item_count

    def __getitem__(self, i):
        if i < 0:
            i += self._item_count
        if 0 <= i < self._item_count:
            offset = (i*self._item_size)
            return self._read_list_item(offset)
        raise IndexError


class Int64List(List):
    def _read_list_item(self, offset):
        return self._read_int64(offset)


class StructList(List):
    def _read_list_item(self, offset):
        return self._itemcls(self._buf, self._offset+offset)
