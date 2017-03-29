import py
import os
import struct
from capnpy.segment import Segment, MultiSegment
from capnpy.type import Types
from capnpy.packing import unpack_primitive
from capnpy.blob import PYX
from capnpy import ptr
from capnpy.struct_ import Struct


def test_tox_PYX():
    tox_env = os.environ.get('TOX_ENV', None)
    if tox_env == 'py27':
        assert PYX
    elif tox_env == 'nopyx':
        assert not PYX

def test_unpack_primitive():
    s = struct.pack('q', 1234)
    assert unpack_primitive(ord('q'), s, 0) == 1234
    #
    # left bound check
    with py.test.raises(IndexError):
        unpack_primitive(ord('q'), s, -8)
    #
    # right bound check
    with py.test.raises(IndexError):
        unpack_primitive(ord('q'), s, 1) # not enough bytes


def test_Segment():
    # buf is an array of int64 == [1, 2]
    buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
           '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
    b1 = Segment(buf)
    assert b1.read_primitive(0, Types.int64.ifmt) == 1
    assert b1.read_primitive(8, Types.int64.ifmt) == 2
    #
    py.test.raises(AssertionError, "Segment(None)")

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

def test_float64():
    buf = '\x58\x39\xb4\xc8\x76\xbe\xf3\x3f'   # 1.234
    b = Segment(buf)
    assert b.read_primitive(0, Types.float64.ifmt) == 1.234

def test_read_ptr():
    buf = '\x90\x01\x00\x00\x02\x00\x04\x00'
    b = Segment(buf)
    p = b.read_ptr(0)
    offset = ptr.deref(p, 0)
    assert offset == 808
    
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
