try:
    import __pypy__
except ImportError:
    # CPython version

    def setslice8(array, offset, s):
        assert len(s) == 8
        assert len(array)-offset >= 8
        array[offset:offset+8] = s

else:
    # PyPy version

    def setslice8(array, offset, s):
        # we need to manual unroll the setslice else PyPy forces the array :-(
        assert len(s) == 8
        array[offset] = s[0]
        array[offset+1] = s[1]
        array[offset+2] = s[2]
        array[offset+3] = s[3]
        array[offset+4] = s[4]
        array[offset+5] = s[5]
        array[offset+6] = s[6]
        array[offset+7] = s[7]
