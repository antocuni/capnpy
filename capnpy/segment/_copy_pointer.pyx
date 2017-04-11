# this is the "pyx part" of _copy_pointer.pyx: it contains things which cannot
# be expressed in pure-python mode, such as cimports and cdef extern from

from libc.stdint cimport int64_t
from capnpy cimport ptr
from capnpy.segment.builder cimport SegmentBuilder
from capnpy.segment.base cimport BaseSegment

# =====================
# BaseSegment speedups
#
# it turns out that calling src.read_int64 and src.check_bounds add a
# significant overhead to copy_pointer, because they are expensive virtual
# calls which does not much in the body. So, we are reimplementing them here,
# in form of fast functions and macros.
#
# Together, they make a 2.1x slowdown!

cdef int64_t read_int64_fast(BaseSegment src, long i):
    return (<int64_t*>(src.cbuf+i))[0]

# check_bounds:
# this is a bit of a hack because apparently it is not possible to define the
# equivalent of C macros in Cython. Earlier, check_bound was a normal cdef
# function which raised if needed. Now, we turned check_bound into a C macro
# with a fast-path (the bound check), and we moved the slow path inside the
# raise_out_of_bound function. This seems to give a ~40% speedup!
cdef extern from "_copy_pointer.h":
    object check_bounds "CHECK_BOUNDS" (BaseSegment src, Py_ssize_t size, Py_ssize_t offset)

cdef object raise_out_of_bounds(Py_ssize_t size, Py_ssize_t offset):
    raise IndexError('Offset out of bounds: %d' % (offset+size))

# ======================
