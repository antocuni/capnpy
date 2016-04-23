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

TUPLE_MAX_LEN = 3

cpdef long tuplehash_1(long h1):
    cdef long len = 1
    cdef long mult = 1000003
    cdef long x = 0x345678
    cdef long y
    # unrolled loop
    # i=1
    y = h1
    x = (x ^ y) * mult
    len -= 1
    mult += <long>(82520 + len + len)
    #
    x += 97531
    if x == -1:
        x = -2
    return x

cpdef long tuplehash_2(long h1, long h2):
    cdef long len = 2
    cdef long mult = 1000003
    cdef long x = 0x345678
    cdef long y
    # unrolled loop
    # i=1
    y = h1
    x = (x ^ y) * mult
    len -= 1
    mult += <long>(82520 + len + len)
    # i=2
    y = h2
    x = (x ^ y) * mult
    len -= 1
    mult += <long>(82520 + len + len)
    #
    x += 97531
    if x == -1:
        x = -2
    return x


cpdef long tuplehash_3(long h1, long h2, long h3):
    cdef long len = 3
    cdef long mult = 1000003
    cdef long x = 0x345678
    cdef long y
    # unrolled loop
    # i=1
    y = h1
    x = (x ^ y) * mult
    len -= 1
    mult += <long>(82520 + len + len)
    # i=2
    y = h2
    x = (x ^ y) * mult
    len -= 1
    mult += <long>(82520 + len + len)
    # i=3
    y = h3
    x = (x ^ y) * mult
    len -= 1
    mult += <long>(82520 + len + len)
    #
    x += 97531
    if x == -1:
        x = -2
    return x
