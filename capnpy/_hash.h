

#include <Python.h>

// duck-typed _Py_HashSecret_t from CPython 2.7 (different from 3.5)
typedef struct {
    long prefix;
    long suffix;
} _Py_HashSecret_custom;

#define MINLONG -9223372036854775807 -1

#if PY_MAJOR_VERSION < 3
    #define HASH_MASK 0
    Py_hash_t strhash_f(const void *src, Py_ssize_t len) {return 0;}
    #define HashSecret _Py_HashSecret
#else
    #define HASH_MASK _PyHASH_MODULUS
    #define strhash_f _Py_HashBytes
    _Py_HashSecret_custom HashSecret; // uninitialized dummy
#endif
