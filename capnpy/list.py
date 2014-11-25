from capnpy.blob import Blob

class List(Blob):

    def __init__(self, buf, offset, item_size, item_count, itemcls):
        Blob.__init__(self, buf, offset)
        self._item_size = item_size
        self._item_count = item_count
        self._itemcls = itemcls

    def _read_list_item(self, offset):
        raise NotImplementedError

class Int64List(List):
    def _read_list_item(self, offset):
        return self._read_int64(offset)
