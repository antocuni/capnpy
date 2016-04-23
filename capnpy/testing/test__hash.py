import py
try:
    from capnpy import _hash
except ImportError:
    py.test.skip('_hash not compiled')

def test_tuplehash():
    assert _hash.tuplehash_1(42) == hash((42,))
    assert _hash.tuplehash_2(42, 43) == hash((42, 43))
    assert _hash.tuplehash_3(42, 43, 44) == hash((42, 43, 44))
