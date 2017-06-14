# The goal of this package is to try hard to use the very same repr as the
# standard capnp decode for float{32,64} fields. It does so by linking to the
# kj library and using the very same underlying algorithm.
#
# By default, capnpy uses the standard python repr for floats. To enable this
# package, you must manually build it by running:
#
#     $ python -m capnpy.floatrepr.build

try:
    from capnpy.floatrepr._floatrepr import ffi, lib
except ImportError:
    raise ImportError("floatrepr not compiled: "
                      "try to run python capnpy/floatrepr/build.py")


# In practice, doubles should never need more than 24 bytes and floats
# should never need more than 14 (including null terminators), but we
# overestimate to be safe.
def float32_repr(x):
    buf = ffi.new('char[24]')
    lib.capnpy_float32_repr(x, buf)
    return ffi.string(buf)

def float64_repr(x):
    buf = ffi.new('char[32]')
    lib.capnpy_float64_repr(x, buf)
    return ffi.string(buf)
