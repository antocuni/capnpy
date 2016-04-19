import cython
from capnpy.unpack cimport unpack_uint32
from capnpy.blob cimport CapnpBuffer
from capnpy.struct_ cimport Struct, struct_from_buffer
from capnpy cimport ptr

# XXX: investigate whether we get any speedup by typing f as BufferedSocket

@cython.locals(msg=Struct)
cpdef load(object f, object payload_type)

cpdef loads(bytes buf, object payload_type)
#cpdef load_all(object f, object payload_type)


@cython.locals(buf = bytes, n=int)
cpdef _load_message(object f)

@cython.locals(buf=bytes, message_size=int, message_lenght=int)
cpdef _load_buffer_single_segment(object f)

@cython.locals(fmt=bytes, size=int, buf=bytes, bytes_read=int,
                padding=int, message_lenght=int, offset=int, size=int)
cpdef _load_buffer_multiple_segments(object f, int n)
