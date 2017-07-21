"""
Reimplementation of CPython's hashing algorithm for many builtin
types. The idea is that if you have C variables, you can compute fast hashes
*without* having to allocate real Python object
"""

cdef extern from "Python.h":
    ctypedef size_t Py_hash_t

    ctypedef Py_hash_t (*hash_f)(const void *, Py_ssize_t)

    ctypedef struct PyHash_FuncDef_t:
        hash_f hash
        const char *name;
        const int hash_bits;
        const int seed_bits;
#    PyHash_FuncDef_t PyHash_FuncDef

    cdef PyHash_FuncDef_t* PyHash_GetFuncDef()

cpdef long strhash(bytes a, long start, long size):
    cdef long maxlen = len(a)
    if start >= maxlen or size == 0:
        return 0
    if size > maxlen:
        size = maxlen-start

    cdef const unsigned char* p = a
    p += start
    return PyHash_GetFuncDef().hash(p, size)


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
