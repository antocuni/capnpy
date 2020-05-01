#include "Python.h"

/* tuplehash implementation on Python >= 3.8 */

#if SIZEOF_PY_UHASH_T > 4
#define _PyHASH_XXPRIME_1 ((Py_uhash_t)11400714785074694791ULL)
#define _PyHASH_XXPRIME_2 ((Py_uhash_t)14029467366897019727ULL)
#define _PyHASH_XXPRIME_5 ((Py_uhash_t)2870177450012600261ULL)
#define _PyHASH_XXROTATE(x) ((x << 31) | (x >> 33))  /* Rotate left 31 bits */
#else
#define _PyHASH_XXPRIME_1 ((Py_uhash_t)2654435761UL)
#define _PyHASH_XXPRIME_2 ((Py_uhash_t)2246822519UL)
#define _PyHASH_XXPRIME_5 ((Py_uhash_t)374761393UL)
#define _PyHASH_XXROTATE(x) ((x << 13) | (x >> 19))  /* Rotate left 13 bits */
#endif

static long
_tuplehash_38(long *hashes, long len)
{
    Py_ssize_t i;
    Py_uhash_t acc = _PyHASH_XXPRIME_5;
    for (i = 0; i < len; i++) {
        Py_uhash_t lane = (Py_uhash_t)hashes[i];
        if (lane == (Py_uhash_t)-1) {
            return -1;
        }
        acc += lane * _PyHASH_XXPRIME_2;
        acc = _PyHASH_XXROTATE(acc);
        acc *= _PyHASH_XXPRIME_1;
    }

    /* Add input length, mangled to keep the historical value of hash(()). */
    acc += len ^ (_PyHASH_XXPRIME_5 ^ 3527539UL);

    if (acc == (Py_uhash_t)-1) {
        return 1546275796;
    }
    return acc;
}
