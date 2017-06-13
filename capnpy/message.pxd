import cython
from capnpy.segment.base cimport unpack_uint32
from capnpy.segment.segment cimport Segment
from capnpy.segment.builder cimport SegmentBuilder
from capnpy.struct_ cimport Struct, struct_from_buffer
from capnpy cimport ptr
from capnpy.filelike cimport FileLike, as_filelike


@cython.locals(msg=Struct, f2=FileLike)
cpdef load(object f, object payload_type)

cpdef loads(bytes buf, object payload_type)
#cpdef load_all(FileLike f, object payload_type)


@cython.locals(buf = bytes, n=int)
cpdef Struct _load_message(FileLike f)

@cython.locals(buf=bytes, message_size=int, message_lenght=int)
cpdef _load_buffer_single_segment(FileLike f)

@cython.locals(fmt=bytes, size=int, buf=bytes, bytes_read=int,
                padding=int, message_lenght=int, offset=int, size=int)
cpdef _load_buffer_multiple_segments(FileLike f, int n)

@cython.locals(builder=SegmentBuilder, segment_size=long, segment_count=long,
               p=long, start=long, end=long)
cpdef dumps(Struct obj, bint fastpath=*)
