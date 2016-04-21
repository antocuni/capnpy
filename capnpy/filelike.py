from capnpy.blob import PYX

def as_filelike(f):
    """
    With Cython: if f is already a FileLike, return it. Else, return the proper
    adapter.

    Without Cython (CPython/PyPy): do nothing and return f
    """
    if PYX:
        # cython-specific logic
        if isinstance(f, FileLike):
            return f
        return FileLikeAdapter(f)
    else:
        # normal logic
        return f


class FileLike(object):
    """
    Base class to represent a file-like object, to be used by message.load()
    and friends.

    In theory, this is completely useless: a lot of existing classes such as
    file, socket._fileobject and StringIO already have the very same
    interface.

    However, the goal of this class is to be compiled by Cython AND to expose
    a C interface to the rest of cython-compiled code (using cpdef
    declarations. This way, we can call f.read() without the cost of doing
    dictionary lookup, argument parsing, etc.
    """

    def read(self, size=-1):
        raise NotImplementedError

    def readline(self):
        raise NotImplementedError


class FileLikeAdapter(FileLike):
    """
    Wrap a general duck-typed file-like object into something which can be
    passed to cython functions which expect an object of type FileLike
    """

    def __init__(self, f):
        self._read = f.read
        self._readline = f.readline

    def read(self, size=-1):
        return self._read(size)

    def readline(self):
        return self._readline
