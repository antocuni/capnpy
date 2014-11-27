try:
    import __pypy__
except ImportError:
    # CPython version

    class StringBuilder(object):

        def __init__(self, sizehint=None):
            self._list = []

        def __check(self):
            if self._list is None:
                raise ValueError, "Can't operate on built builder"

        def append(self, chunk):
            self.__check()
            self._list.append(chunk)

        def build(self):
            result = ''.join(self._list)
            self._list = None
            return result

else:
    # PyPy version
    from __pypy__.builders import StringBuilder

