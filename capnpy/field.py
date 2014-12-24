class Primitive(object):

    def __init__(self, offset, type):
        self.offset = offset
        self.type = type

    def __get__(self, blob, cls):
        if blob is None:
            return self
        return blob._read_primitive(self.offset, self.type)

    def __repr__(self):
        return '<Field: Primitive, offset=%d, type=%r>' % (self.offset, self.type)
        

class String(object):

    def __init__(self, offset):
        self.offset = offset

    def __get__(self, blob, cls):
        if blob is None:
            return self
        return blob._read_string(self.offset)

    def __repr__(self):
        return '<Field: String, offset=%d>' % (self.offset,)


class List(object):

    def __init__(self, offset, listcls, item_type):
        self.offset = offset
        self.listcls = listcls
        self.item_type = item_type

    def __get__(self, blob, cls):
        if blob is None:
            return self
        return blob._read_list(self.offset, self.listcls, self.item_type)

    def __repr__(self):
        return ('<Field: List, offset=%d, listcls=%s, item_type=%r>' %
                (self.offset, self.listcls.__name__, self.item_type))
