import struct

def decode_message(bytes, rootcls):
    msg = Message(bytes, rootcls)
    return msg.root.value

def ptrderef(buf, offset):
    ptr = struct.unpack_from('=q', buf, offset)[0]
    ptr_offset = (ptr & 0xfffffffc) >> 2
    return offset + (ptr_offset+1)*8


class AbstractStruct(object):
    
    def __init__(self, buf, offset):
        self._buf = buf
        self._offset = offset

    @classmethod
    def from_pointer(cls, buf, offset, *args, **kwds):
        offset = ptrderef(buf, offset)
        return cls(buf, offset, *args, **kwds)

    def _read_int64(self, offset):
        return struct.unpack_from('=q', self._buf, offset+self._offset)[0]


class Message(object):
    def __init__(self, buf, rootcls):
        self._buf = buf
        self._rootcls = rootcls

    @property
    def root(self):
        return MessageRoot.from_pointer(self._buf, 0, self._rootcls)



class MessageRoot(AbstractStruct):

    def __init__(self, buf, offset, rootcls):
        AbstractStruct.__init__(self, buf, offset)
        self._rootcls = rootcls

    @property
    def value(self):
        return self._rootcls.from_pointer(self._buf, self._offset+0)



# ===============================================================================
# point.capnp specific part: in theory, it should all be automatically generated
# ===============================================================================

class Point(AbstractStruct):
    
    @property
    def x(self):
        return self._read_int64(0)

    @property
    def y(self):
        return self._read_int64(8)


class Rectangle(AbstractStruct):


    # return "by ref" (i.e. by passing a ref to the original buffer and a offset)
    @property
    def a(self):
        return Point.from_pointer(self._buf, self._offset+0)

    @property
    def b(self):
        return Point.from_pointer(self._buf, self._offset+8)

    # return "by val" (i.e. by copying a slice of the original buffer)
    @property
    def a_byval(self):
        offset = ptrderef(self._buf, self._offset+0)
        newbuf = self._buf[offset:offset+16]
        return Point(newbuf, 0)

    @property
    def b_byval(self):
        offset = ptrderef(self._buf, self._offset+8)
        newbuf = self._buf[offset:offset+16]
        return Point(newbuf, 0)
