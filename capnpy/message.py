from capnpy.blob import Blob

def loads(buf, payload_type):
    """
    Decode the capnp message in buf, using the given payload type.
    payload_type is expected to be a struct.
    """
    m = Message(buf)
    return m.get_struct(payload_type)


class Message(object):
    """
    Represent a full capnp message.

    Glossary:

      - Message: the whole array-of-bytes; it starts with a pointer to an
        anonymous struct with only one field, called ``root``

      - root: the struct whose only field contains the actual payload; most of
        the time, it's a pointer to a struct, but we don't know its type
        statically

      - payload: the data contained in the root's field

    The various get_* methods are used to interpret the payload as
    required. For example, if we know the payload is a struct, we will use
    get_struct(). Since capnp does not support introspection, there is no way
    to query the type of the payload in case we don't know it.
    """

    def __init__(self, buf):
        blob = Blob.from_buffer(buf, 0)
        self._root = blob._read_struct(0, Blob)

    def get_struct(self, structcls):
        """
        Read the payload as if it were a pointer to ``structcls``
        """
        return self._root._read_struct(0, structcls)
