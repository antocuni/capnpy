from capnpy.segment.base import BaseSegment
from capnpy import ptr
from capnpy import _hash
from capnpy.printer import print_buffer, BufferPrinter


class Segment(BaseSegment):
    """
    Represent a capnproto buffer for a single-segment message. Far pointers are
    not allowed here
    """

    def __reduce__(self):
        # pickle support
        return Segment, (self.buf,)

    def read_ptr(self, offset):
        """
        Return the pointer at the specifield offet.

        WARNING: you MUST check whether the returned pointer is FAR, and in
        that case call again read_far_ptr, which handles FAR pointers
        correctly but it is much slower than this. We need this messy interface for
        speed; the proper alternative would be to simply return a tuple
        (offset, p) and handle the far ptr here: this is fine on PyPy but slow
        on CPython, because this way we cannot give a static return type.

        Or, we could raise an exception to signal that we found a FAR
        pointer. However, this would be ~20% slower than the current approach.
        """
        return self.read_int64(offset)

    def read_far_ptr(self, offset):
        raise ValueError("Cannot read a far pointer inside a single-segment message")

    def read_str(self, p, offset, default_, additional_size):
        """
        Read Text or Data from the pointer ``p``, which was read from the given
        offset.

        If you want to read a Text, pass additional_size=-1 to remove the
        trailing '\0'. If you want to read a Data, pass additional_size=0.
        """
        if p == 0:
            return default_
        assert ptr.kind(p) == ptr.LIST
        assert ptr.list_size_tag(p) == ptr.LIST_SIZE_8
        start = ptr.deref(p, offset)
        end = start + ptr.list_item_count(p) + additional_size
        return self.buf[start:end]

    def hash_str(self, p, offset, default_, additional_size):
        if p == 0:
            return default_
        assert ptr.kind(p) == ptr.LIST
        assert ptr.list_size_tag(p) == ptr.LIST_SIZE_8
        start = ptr.deref(p, offset)
        size = ptr.list_item_count(p) + additional_size
        return _hash.strhash(self.buf, start, size)

    def _print(self, **kwds):
        p = BufferPrinter(self.buf)
        p.printbuf(start=0, end=None, **kwds)


class MultiSegment(Segment):
    """
    Represent a capnproto buffer for a multiple segments message. The segments
    are stored in a single consecutive area of memory, and segment_offsets
    stores the offset at which each segment starts.
    """

    def __init__(self, s, segment_offsets):
        assert segment_offsets is not None
        super(MultiSegment, self).__init__(s)
        self.segment_offsets = segment_offsets

    def __reduce__(self):
        # pickle support
        return MultiSegment, (self.buf, self.segment_offsets)

    def read_far_ptr(self, offset):
        """
        Read and return the ptr referenced by this far pointer
        """
        p = self.read_ptr(offset)
        segment_start = self.segment_offsets[ptr.far_target(p)] # in bytes
        offset  = segment_start + ptr.far_offset(p)*8
        if ptr.far_landing_pad(p) == 0:
            # simple case: the landing pad is a normal pointer, just read it
            p = self.read_ptr(offset)
            return offset, p
        else:
            # complex case. From capnproto specs:
            #     If B == 1, then the "landing pad" is itself another far
            #     pointer that is interpreted differently: This far pointer
            #     (which always has B = 0) points to the start of the object's
            #     content, located in some other segment. The landing pad is
            #     itself immediately followed by a tag word. The tag word
            #     looks exactly like an intra-segment pointer to the target
            #     object would look, except that the offset is always zero.
            #
            # read the 2nd far pointer and the tag word
            p = self.read_ptr(offset)
            ptag = self.read_ptr(offset+8)
            assert ptr.kind(p) == ptr.FAR
            assert ptr.far_landing_pad(p) == 0
            assert ptr.offset(ptag) == 0
            # compute the absolute offset which the object is located at
            segment_start = self.segment_offsets[ptr.far_target(p)] # in bytes
            offset  = segment_start + ptr.far_offset(p)*8
            #
            # ptag is a pointer which perfectly describes the object we want
            # to read. Remember that normally when ptr_offset==0, capnproto
            # expects the object to start at offset+8. So here we return
            # offset-8, so that the object will be read at the expected place
            return offset-8, ptag
