"""
Reimplementation of CPython's hashing algorithm for many builtin
types. The idea is that if you have C variables, you can compute fast hashes
*without* having to allocate real Python object
"""

cdef extern from "Python.h":
    ctypedef struct _Py_HashSecret_t:
        long prefix
        long suffix
    _Py_HashSecret_t _Py_HashSecret


cpdef long inthash(long v):
    if v == -1:
        return -2
    return v

cpdef long longhash(unsigned long v):
    return inthash(<long>v)


# string hashing algorithm. Copied from CPython's 2.7 stringobject.c. Note
# that in Python 3 the hash function is different.
# The invariant is: strhash(s, i, n) == hash(s[i:i+n]) (assuming size>=0)
cpdef long strhash(bytes a, long start, long size):
    cdef long maxlen = len(a)
    if start > maxlen or size == 0:
        return 0
    if size > maxlen:
        size = maxlen-start
    #
    cdef const unsigned char* p = a
    cdef long n = size
    cdef long x
    #
    p += start
    x = _Py_HashSecret.prefix
    x ^= p[0]<<7
    while True:
        n -= 1
        if n < 0:
            break
        x = (1000003*x) ^ p[0]
        p += 1
    x ^= size
    x ^= _Py_HashSecret.suffix
    if x == -1:
        x = -2
    return x

# tuple hashing algorithm. The magic numbers and the algorithm itself are
# taken from python/Objects/tupleobject.c:tuplehash

# Cython-only interface
cdef long tuplehash(long hashes[], long len):
    cdef long mult = 1000003
    cdef long x = 0x345678
    cdef long y
    while True:
        len -= 1
        if len < 0:
            break
        # equivalent to y = *hashes++
        y = hashes[0]
        hashes += 1
        #
        x = (x ^ y) * mult
        mult += <long>(82520 + len + len)
    #
    x += 97531
    if x == -1:
        x = -2
    return x


# Python interface, used by tests
from cpython cimport array
import array
cpdef long __tuplehash_for_tests(object hashes):
    cdef array.array a = array.array('l', hashes)
    return tuplehash(a.data.as_longs, len(a))
