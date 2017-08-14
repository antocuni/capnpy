import py
import os
import struct
from capnpy.segment.segment import Segment, MultiSegment
from capnpy.type import Types
from capnpy.packing import unpack_primitive
from capnpy.blob import PYX
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


    
