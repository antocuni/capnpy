import struct
from capnpy.segment.base import unpack_uint32
from capnpy.segment.segment import Segment, MultiSegment
from capnpy.segment.builder import SegmentBuilder
from capnpy.struct_ import Struct, struct_from_buffer
from capnpy import ptr
from capnpy.filelike import as_filelike
from capnpy.buffered import StringBuffer


def load(f, payload_type):
    """
    Load a message of type ``payload_type`` from f.

    The message is encoded using the recommended capnp format for serializing
    messages over a stream:

      - (4 bytes) The number of segments, minus one (since there is always at
        least one segment)
    
      - (N * 4 bytes) The size of each segment, in words.
    
      - (0 or 4 bytes) Padding up to the next word boundary.

      - The content of each segment, in order.
    """
    f2 = as_filelike(f)
    msg = _load_message(f2)
    return msg._read_struct(0, payload_type)

def loads(buf, payload_type):
    """
    Same as load(), but load from a string instead of a file
    """
    f = StringBuffer(buf)
    obj = load(f, payload_type)
    if f.tell() != len(buf):
        remaining = len(buf)-f.tell()
        raise ValueError("Not all bytes were consumed: %d bytes left" % remaining)
    return obj

def load_all(f, payload_type):
    """
    Load and yield all the messages in the given file-like object
    """
    try:
        while True:
            yield load(f, payload_type)
    except EOFError:
        pass

def _load_message(f):
    # read the total number of segments
    buf = f.read(4)
    if len(buf) < 4:
        raise EOFError("No message to load")
    n = unpack_uint32(buf, 0) + 1
    if n == 1:
        capnp_buf = _load_buffer_single_segment(f) # fast path
    else:
        capnp_buf = _load_buffer_multiple_segments(f, n) # slow path
    #
    # from the capnproto docs:
    #
    #     The first word of the first segment of the message is always a
    #     pointer pointing to the message's root struct.
    #
    # Thus, the root of the message is equivalent to a struct with
    # data_size==0 and ptrs_size==1
    return struct_from_buffer(Struct, capnp_buf, 0, data_size=0, ptrs_size=1)


def _load_buffer_single_segment(f):
    # fast path for the single-segment case. In this scenario, we don't
    # even need to compute the padding as we know that we read exactly 4+4
    # bytes
    buf = f.read(4)
    #
    # The cost of the len(buf) checks is ~7-8% on CPython, but I don't know
    # how to avoid it. However, it's negligible on PyPy
    if len(buf) < 4:
        raise ValueError("Unexpected EOF when reading the header")
    message_size = unpack_uint32(buf, 0)
    message_lenght = message_size * 8
    buf = f.read(message_lenght)
    if len(buf) < message_lenght:
        raise ValueError("Unexpected EOF: expected %d bytes, got only %s. " 
                         "Segment size: %s" % (message_lenght, len(buf), message_size))
    return Segment(buf)

def _load_buffer_multiple_segments(f, n):
    # slow path for the multiple-segments case
    #
    # 1. read the size of each segment
    segments = []
    fmt = b'<I'
    size = struct.calcsize(fmt)
    for i in xrange(n):
        buf = f.read(size)
        if len(buf) < size:
            raise ValueError("Unexpected EOF when reading the header")
        segments.append(struct.unpack(fmt, buf)[0])
    #
    # 2. add enough padding so that the message starts at word boundary
    bytes_read = 4 + n*4 # 4 bytes for the n, plus 4 bytes for each segment
    if bytes_read % 8 != 0:
        padding = 8-(bytes_read % 8)
        f.read(padding)
    #
    # 3. read the body of the message
    message_lenght = sum(segments)*8
    buf = f.read(message_lenght)
    if len(buf) < message_lenght:
        raise ValueError("Unexpected EOF: expected %d bytes, got only %s. "
                         "Segments size: %s" % (message_lenght, len(buf), segments))
    #
    # 4. precompute the offset of each segment starting from the beginning of buf
    segment_offsets = []
    segment_offsets.append(0)
    offset = 0
    for size in segments[:-1]:
        offset += size*8
        segment_offsets.append(offset)
    #
    # 5. we are finally done :)
    return MultiSegment(buf, tuple(segment_offsets))

def dumps(obj, fastpath=True):
    """
    Dump a struct into a message, returned as a string of bytes.

    The message is encoded using the recommended capnp format for serializing
    messages over a stream. It always uses a single segment.

    By default, it tries to follow a fast path: it checks if the object is
    "compact" (as defined by capnpy/visit.py) and, is so, uses a fast memcpy
    to dump the whole message.

    If the fast path can be taken, it is approximately 5x faster on CPython
    and 10x faster on PyPy. However, if the object is **not** compact, the
    fast path check makes it ~2x slower. If you are sure that the object is
    not compact, you can disable the check by passing ``fastpath=False``.
    """
    if fastpath:
        # try the fast path: if the object is compact, we can dump the
        # object with a fast memcpy
        end = obj._get_end()
    else:
        end = -1
    #
    if end != -1:
        # fast path. On CPython, the real speedup comes from the fact that we
        # do not create a temporary SegmentBuilder. The memcpy vs copy_pointer
        # difference seems negligible, for small objects at least.
        start = obj._data_offset
        p = ptr.new_struct(0, obj._data_size, obj._ptrs_size)
        return obj._seg.dump_message(p, start, end)
    else:
        builder = SegmentBuilder()
        builder.allocate(16) # reserve space for segment header+the root pointer
        builder.copy_from_struct(8, Struct, obj)
        segment_count = 1
        segment_size = (builder.get_length()-8) / 8 # subtract the segment header
                                                    # and convert to words
        builder.write_uint32(0, segment_count - 1)
        builder.write_uint32(4, segment_size)
        return builder.as_string()

def dump(obj, f, fastpath=True):
    """
    Same as dumps, but write to the specified file instead of returning a
    string
    """
    f.write(dumps(obj, fastpath))
