import py
import sys
try:
    from capnpy import _hash
except ImportError:
    py.test.skip('_hash not compiled')

def test_inthash():
    h = _hash.inthash
    assert h(42) == hash(42)
    assert h(-1) == hash(-1)
    assert h(-2) == hash(-2)
    assert h(sys.maxint) == hash(sys.maxint)
    assert h(-sys.maxint-1) == hash(-sys.maxint-1)

def test_longhash():
    h = _hash.longhash
    # these are easy
    assert h(42) == hash(42)
    assert h(sys.maxint) == hash(sys.maxint)
    #
    # these are real longs
    assert h(sys.maxint+1) == hash(sys.maxint+1)
    maxulong = sys.maxint*2 + 1
    assert h(maxulong) == hash(maxulong) == hash(-1)


def test_tuplehash():
    assert _hash.tuplehash_1(42) == hash((42,))
    assert _hash.tuplehash_2(42, 43) == hash((42, 43))
    assert _hash.tuplehash_3(42, 43, 44) == hash((42, 43, 44))
