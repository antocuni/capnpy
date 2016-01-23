import py
import cffi
ffi = cffi.FFI()

DIR = py.path.local(__file__).dirpath()

ffi.cdef("""
    void capnpy_float32_repr(float x, char* buffer);
    void capnpy_float64_repr(double x, char* buffer);
""")

ffi.set_source("_floatrepr",
    """
    void capnpy_float32_repr(float x, char* buffer);
    void capnpy_float64_repr(double x, char* buffer); 
    """,
    sources = ['kjwrap.cc'],
    extra_compile_args = ['--std=c++11'],
    libraries = ['kj'],
)

if __name__ == "__main__":
    DIR.chdir()
    ffi.compile()
    # remove leftovers
    DIR.join('_floatrepr.c').remove()
    DIR.join('_floatrepr.o').remove()
    DIR.join('kjwrap.o').remove()

