// XXX: how to avoid to hard-copy the C name generated for raise_out_of_bound?
#define RAISE_OUT_OF_BOUND __pyx_f_6capnpy_7segment_7builder_raise_out_of_bound
static long RAISE_OUT_OF_BOUND(long, long, Py_ssize_t);

#define CHECK_BOUND(pos, n, src_len)                                    \
    0; /* return non-error value by default */                          \
    {                                                                   \
        if ((pos)+(n) > (src_len)) {                                    \
            /* raise and return error */                                \
            return RAISE_OUT_OF_BOUND((pos), (n), (src_len));           \
        }                                                               \
    }
