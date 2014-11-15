import cffi
ffi = cffi.FFI()
ffi.cdef("""
    typedef struct {
        unsigned int kind:2;
        unsigned int offset:30;
        unsigned int data_size:16;
        unsigned int ptr_size:16;
    } Ptr;

    typedef struct {
        Ptr root; // MessageRoot*
    } Message;

    typedef struct {
        Ptr value;
    } MessageRoot;
""")

def decode_message(bytes, rootcls):
    msg = Message(bytes, rootcls)
    return msg.root.value

def ptrderef(p):
    p = ffi.addressof(p)
    buf = ffi.cast('char*', p)
    offset = p.offset+1
    return buf + offset*8

def ptrshow(p):
    print ('Ptr(kind=%d, offset=%d, data_size=%d, ptr_size=%d)' %
           (p.kind, p.offset, p.data_size, p.ptr_size))


class AbstractStruct(object):
    ctype = None
    
    def __init__(self, ptr, message):
        self._message = message # the whole message: needed to keepalive the original buf
        buf = ptrderef(ptr)
        self._obj = self.ffi.cast(self.ctype, buf)


class Message(object):
    def __init__(self, bytes, rootcls):
        self._buf = ffi.new('char[]', len(bytes))
        self._buf[0:len(bytes)] = bytes
        self._rootcls = rootcls
        self._obj = ffi.cast('Message*', self._buf)

    @property
    def root(self):
        return MessageRoot(self._obj.root, self, self._rootcls)



class MessageRoot(AbstractStruct):
    ffi = ffi
    ctype = 'MessageRoot*'

    def __init__(self, ptr, message, rootcls):
        AbstractStruct.__init__(self, ptr, message)
        self._rootcls = rootcls

    @property
    def value(self):
        return self._rootcls(self._obj.value, self._message)



# ===============================================================================
# point.capnp specific part: in theory, it should all be automatically generated
# ===============================================================================

ffi.cdef("""
    typedef struct {
        int64_t x;
        int64_t y;
    } Point;

    typedef struct {
        Ptr a; // Point*
        Ptr b; // Point*
    } Rectangle;
""")


class Point(AbstractStruct):
    ffi = ffi
    ctype = 'Point*'

    @property
    def x(self):
        return self._obj.x

    @property
    def y(self):
        return self._obj.y


class Rectangle(AbstractStruct):
    ffi = ffi
    ctype = 'Rectangle*'

    @property
    def a(self):
        return Point(self._obj.a, self._message)

    @property
    def b(self):
        return Point(self._obj.b, self._message)

