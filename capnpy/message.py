import struct
from capnpy.blob import Blob

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
    total_size = sum(segments)*8 + offset
    if len(buf) != total_size:
        raise ValueError("The length of the buffer does not correspond to the length of "
                         "the segments %s: expected %s, got %s" %
                         (segments, total_size, len(buf)))
    msg = Blob.from_buffer(buf, offset)
    return msg._read_struct(0, payload_type)
