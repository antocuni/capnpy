import py
from capnpy import ptr
from capnpy.segment.segment import Segment, MultiSegment

def test_Segment_pickle():
    import cPickle as pickle
    buf = Segment('hello')
    #
    buf2 = pickle.loads(pickle.dumps(buf))
    assert buf2.buf == 'hello'
    #
    buf2 = pickle.loads(pickle.dumps(buf, pickle.HIGHEST_PROTOCOL))
    assert buf2.buf == 'hello'

def test_MultiSegment_pickle():
    import cPickle as pickle
    buf = MultiSegment('hello', (1, 2, 3))
    #
    buf2 = pickle.loads(pickle.dumps(buf))
    assert buf2.buf == 'hello'
    assert buf2.segment_offsets == (1, 2, 3)
    #
    buf2 = pickle.loads(pickle.dumps(buf, pickle.HIGHEST_PROTOCOL))
    assert buf2.buf == 'hello'
    assert buf2.segment_offsets == (1, 2, 3)

def test_read_str():
    buf = ('garbage0'
           'hello capnproto\0') # string
    p = ptr.new_list(0, ptr.LIST_SIZE_8, 16)
    b = Segment(buf)
    s = b.read_str(p, 0, "", additional_size=-1)
    assert s == "hello capnproto"
    s = b.read_str(p, 0, "", additional_size=0)
    assert s == "hello capnproto\0"

def test_hash_str():
    buf = ('garbage0'
           'hello capnproto\0') # string
    p = ptr.new_list(0, ptr.LIST_SIZE_8, 16)
    b = Segment(buf)
    h = b.hash_str(p, 0, 0, additional_size=-1)
    assert h == hash("hello capnproto")
    h = b.hash_str(p, 0, 0, additional_size=0)
    assert h == hash("hello capnproto\0")

def test_hash_str_exception():
    buf = ''
    p = ptr.new_struct(0, 1, 1) # this is the wrong type of pointer
    b = Segment(buf)
    py.test.raises(AssertionError, "b.hash_str(p, 0, 0, 0)")
