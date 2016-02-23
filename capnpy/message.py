import struct
from cStringIO import StringIO
from capnpy.blob import CapnpBuffer
from capnpy.struct_ import Struct
from capnpy import ptr

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
    msg = _load_message(f)
    return msg._read_struct(0, payload_type)

def loads(buf, payload_type):
    """
    Same as load(), but load from a string instead of a file
    """
    f = StringIO(buf)
    obj = load(f, payload_type)
    if f.tell() != len(buf):
        remaining = len(buf)-f.tell()
        raise ValueError("Not all bytes were consumed: %d bytes left" % remaining)
    return obj

def _unpack_from_file(fmt, f):
    size = struct.calcsize(fmt)
    buf = f.read(size)
    if len(buf) < size:
        raise ValueError("Unexpected EOF when reading the header")
    return struct.unpack(fmt, buf)

def _load_message(f):
    # total number of segments
    n = _unpack_from_file('<I', f)[0] + 1
    segments = _unpack_from_file('<'+'I'*n, f)
    #
    # add enough padding so that the message starts at word boundary
    bytes_read = 4 + n*4 # 4 bytes for the n, plus 4 bytes for each segment
    if bytes_read % 8 != 0:
        padding = 8-(bytes_read % 8)
        f.read(padding)
    #
    message_lenght = sum(segments)*8
    buf = f.read(message_lenght)
    if len(buf) < message_lenght:
        raise ValueError("Unexpected EOF: expected %d bytes, got only %s. "
                         "Segments size: %s" % (message_lenght, len(buf), segments))

    # precompute the offset of each segment starting from the beginning of buf
    segment_offsets = []
    segment_offsets.append(0)
    offset = 0
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
    buf = CapnpBuffer(buf, tuple(segment_offsets))
    return Struct.from_buffer(buf, 0, data_size=0, ptrs_size=1)

def dumps(obj):
    """
    Dump a struct into a message, returned as a string of bytes.

    The message is encoded using the recommended capnp format for serializing
    messages over a stream. It always uses a single segment.
    """
    a = obj._get_body_start()
    b = obj._get_extra_end()
    buf = obj._buf.s[a:b]
    p = ptr.new_struct(0, obj._data_size, obj._ptrs_size)
    #
    segment_count = 1
    if len(buf) % 8 != 0:
        padding = 8 - (len(buf) % 8)
        buf += '\x00' * padding
    segment_size = len(buf)/8 + 1 # +1 is for the ptr
    header = struct.pack('iiQ', segment_count-1, segment_size, p)
    return header + buf

