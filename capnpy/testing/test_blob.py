import py
import os
import struct
from capnpy.segment.segment import Segment, MultiSegment
from capnpy.type import Types
from capnpy.packing import unpack_primitive
from capnpy.blob import PYX
from capnpy.struct_ import Struct


def test_tox_PYX():
    tox_env = os.environ.get('TOX_ENV', '')
    if 'py27' in tox_env:
        assert PYX
    elif 'nopyx' in tox_env:
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


    
