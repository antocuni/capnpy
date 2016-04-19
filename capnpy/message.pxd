import cython
from capnpy.unpack cimport unpack_uint32
from capnpy.blob cimport CapnpBuffer
from capnpy.struct_ cimport Struct
from capnpy cimport ptr

# XXX: investigate whether we get any speedup by typing f as BufferedSocket
cpdef load(object f, object payload_type)
cdef _unpack_segments(object f, int n)

@cython.locals(buf = bytes, n=int, bytes_read=int)
cpdef _load_message(object f)

