"""
Reimplementation of CPython's hashing algorithm for many builtin
types. The idea is that if you have C variables, you can compute fast hashes
*without* having to allocate real Python object
"""

cpdef long inthash(long v):
    if v == -1:
        return -2
    return v

cpdef long longhash(unsigned long v):
    return inthash(<long>v)


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
