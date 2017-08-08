/* This is a workaround for conditional cimport from cpython.string
   or cpython.bytes in Python 2 or Python 3 respectively. */

#if PY_MAJOR_VERSION < 3
    #define _PyString_GET_SIZE PyString_GET_SIZE
    #define _PyString_AS_STRING PyString_AS_STRING
    #define _PyString_CheckExact PyString_CheckExact
    #define _PyString_FromStringAndSize PyString_FromStringAndSize
#else
    #define _PyString_GET_SIZE PyBytes_GET_SIZE
    #define _PyString_AS_STRING PyBytes_AS_STRING
    #define _PyString_CheckExact PyBytes_CheckExact
    #define _PyString_FromStringAndSize PyBytes_FromStringAndSize
#endif
