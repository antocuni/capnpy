import struct
from capnpy.struct_ import Struct
from capnpy.ptr import StructPtr


def loads(buf, payload_type):
    """
    Load a message of type ``payload_type`` from buf.

    The message is encoded using the recommended capnp format for serializing
    messages over a stream:

      - (4 bytes) The number of segments, minus one (since there is always at
        least one segment)
    
      - (N * 4 bytes) The size of each segment, in words.
    
      - (0 or 4 bytes) Padding up to the next word boundary.

      - The content of each segment, in order.
    """
    msg = _load_message(buf)
    return msg._read_struct(0, payload_type)

def _load_message(buf):
    offset = 0
    # total number of segments
    n = struct.unpack_from('<I', buf, offset)[0] + 1
    offset += 4
    fmt = '<' + ('I'*n)
    segments = struct.unpack_from(fmt, buf, offset) # size of each segment
    offset += 4*n
    #
    # add enough padding so that the message starts at word boundary
    if offset % 8 != 0:
        padding = 8-(offset % 8)
        offset += padding
    #
    message_offset = offset
    total_size = sum(segments)*8 + message_offset
    if len(buf) != total_size:
        raise ValueError("The length of the buffer does not correspond to the length of "
                         "the segments %s: expected %s, got %s" %
                         (segments, total_size, len(buf)))

    # precompute the offset of each segment starting from the beginning of buf
    segment_offsets = []
    segment_offsets.append(message_offset)
    for size in segments[:-1]:
        offset += size*8
        segment_offsets.append(offset)

    # from the capnproto docs:
    #
    #     The first word of the first segment of the message is always a
    #     pointer pointing to the message's root struct.
    #
    # Thus, the root of the message is equivalent to a struct with
    # data_size==0 and ptrs_size==1
    return Struct.from_buffer(buf, message_offset, tuple(segment_offsets),
                              data_size=0, ptrs_size=1)

def dumps(obj):
    """
    Dump a struct into a message, returned as a string of bytes.

    The message is encoded using the recommended capnp format for serializing
    messages over a stream. It always uses a single segment.
    """
    a = obj._get_body_start()
    b = obj._get_extra_end()
    buf = obj._buf[a:b]
    ptr = StructPtr.new(0, obj._data_size, obj._ptrs_size)
    #
    segment_count = 1
    if len(buf) % 8 != 0:
        padding = 8 - (len(buf) % 8)
        buf += '\x00' * padding
    segment_size = len(buf)/8 + 1 # +1 is for the ptr
    header = struct.pack('iiQ', segment_count-1, segment_size, ptr)
    return header + buf

