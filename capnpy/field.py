class Primitive(object):

    def __init__(self, offset, type):
        self.offset = offset
        self.type = type

    def __get__(self, blob, cls):
        if blob is None:
            return self
        return blob._read_primitive(self.offset, self.type)

    def __repr__(self):
        return 'Primitive(offset=%d, type=%r)' % (self.offset, self.type)
        
