

#include <Python.h>

typedef struct {
    long prefix;
    long suffix;
} _Py_HashSecret_custom;

#define MINLONG -9223372036854775808

#if PY_MAJOR_VERSION < 3

    #define HASH_MASK 0
    Py_hash_t strhash_f(const void *src, Py_ssize_t len) {return 0;}
    #define HashSecret _Py_HashSecret

#else

    #define strhash_f _Py_HashBytes
    _Py_HashSecret_custom HashSecret;
    #define HASH_MASK _PyHASH_MODULUS

#endif
