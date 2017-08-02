// XXX: how to avoid to hard-copy the C name generated for raise_out_of_bound?
#define RAISE_OUT_OF_BOUNDS __pyx_f_6capnpy_7segment_7builder_raise_out_of_bounds
static PyObject* RAISE_OUT_OF_BOUNDS(Py_ssize_t, Py_ssize_t);

#if PY_MAJOR_VERSION < 3
#   define GET_SIZE PyString_GET_SIZE
#else
#   define GET_SIZE PyBytes_GET_SIZE
#endif

#define CHECK_BOUNDS(src, size, offset)                                 \
    (Py_INCREF(Py_None), Py_None);                                      \
    {                                                                   \
        if ((offset)+(size) > (GET_SIZE(src->buf))) {                   \
            /* raise and return error */                                \
            return RAISE_OUT_OF_BOUNDS(size, offset);                   \
        }                                                               \
    }
