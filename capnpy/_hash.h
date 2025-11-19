#include <Python.h>

/* Duck-typed _Py_HashSecret_t from CPython 2.7. This struct is different in
   CPython 3.5 so including it directly causes errors, as prefix and suffix
   fields are non-existent. This allows for cython compilation and linking
   of _hash.pyx to be possible in both Python 2 and 3 at the same time.
*/
typedef struct {
    long prefix;
    long suffix;
} _Py_HashSecret_custom;

#define MINLONG (-9223372036854775807 - 1)

#if PY_MAJOR_VERSION < 3

    // Use _Py_HashSecret from CPython 2.7
    #define HashSecret _Py_HashSecret

    // Unused in Python 2, but has to exist during cython compilation
    #define HASH_MASK 0
    Py_hash_t strhash_f(const void *src, Py_ssize_t len) { return 0; }

#else

    // Use values / methods from CPython 3.5
    #define HASH_MASK _PyHASH_MODULUS

    // https://groups.google.com/g/cython-users/c/YQkU8oc8oSM/m/nVJ_IX8KAgAJ
    #if PY_VERSION_HEX < 0x030E0000
    #define strhash_f _Py_HashBytes
    #else
    #define strhash_f Py_HashBuffer
    #endif

    // Unused in Python 3, but has to exist during cython compilation
    _Py_HashSecret_custom HashSecret;

    // Required for 3.13 because it's now hidden and C will assume the
    // return type is int rather than long
    #if PY_VERSION_HEX > 0x030D0000 && PY_VERSION_HEX < 0x030E0000
    Py_hash_t _Py_HashBytes(const void *src, Py_ssize_t len);
    #endif

#endif
