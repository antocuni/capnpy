from cStringIO import StringIO
from capnpy.blob import PYX
from capnpy.filelike import as_filelike, FileLike


def test_as_filelike():
    buf = StringIO('hello')
    f = as_filelike(buf)
    if PYX:
        assert isinstance(f, FileLike)
    else:
        assert f is buf
    assert f.read(8) == 'hello'
