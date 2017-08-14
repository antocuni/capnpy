import py
from six import b

from capnpy import ptr
from capnpy.segment.segment import Segment, MultiSegment

def test_Segment_pickle():
    import pickle
    buf = Segment(b'hello')
    #
    buf2 = pickle.loads(pickle.dumps(buf))
    assert buf2.buf == b'hello'
    #
    buf2 = pickle.loads(pickle.dumps(buf, pickle.HIGHEST_PROTOCOL))
    assert buf2.buf == b'hello'

def test_MultiSegment_pickle():
    import pickle
    buf = MultiSegment(b'hello', (1, 2, 3))
    #
    buf2 = pickle.loads(pickle.dumps(buf))
    assert buf2.buf == b'hello'
    assert buf2.segment_offsets == (1, 2, 3)
    #
    buf2 = pickle.loads(pickle.dumps(buf, pickle.HIGHEST_PROTOCOL))
    assert buf2.buf == b'hello'
    assert buf2.segment_offsets == (1, 2, 3)

def test_read_str():
    buf = b('garbage0'
            'hello capnproto\0') # string
    p = ptr.new_list(0, ptr.LIST_SIZE_8, 16)
    bb = Segment(buf)
    s = bb.read_str(p, 0, "", additional_size=-1)
    assert s == b"hello capnproto"
    s = bb.read_str(p, 0, "", additional_size=0)
    assert s == b"hello capnproto\0"

def test_hash_str():
    buf = b('garbage0'
            'hello capnproto\0') # string
    p = ptr.new_list(0, ptr.LIST_SIZE_8, 16)
    bb = Segment(buf)
    h = bb.hash_str(p, 0, 0, additional_size=-1)
    assert h == hash(b"hello capnproto")
    h = bb.hash_str(p, 0, 0, additional_size=0)
    assert h == hash(b"hello capnproto\0")

def test_hash_str_exception():
    buf = b''
    p = ptr.new_struct(0, 1, 1) # this is the wrong type of pointer
    bb = Segment(buf)
    py.test.raises(AssertionError, "bb.hash_str(p, 0, 0, 0)")
