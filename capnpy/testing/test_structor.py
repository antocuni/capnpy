from capnpy.blob import Blob
from capnpy.structor import structor, compute_format
from capnpy import field
from capnpy.type import Types

class FakeBlob(object):

    @classmethod
    def from_buffer(cls, buf, offset, segment_offsets):
        return buf



def test_compute_format_simple():
    fields = [field.Primitive(0, Types.int64),
              field.Primitive(8, Types.int64)]
    fmt = compute_format(data_size=2, ptrs_size=0, fields=fields)
    assert fmt == 'qq'

def test_compute_format_holes():
    fields = [field.Primitive(0, Types.int32),
              field.Primitive(8, Types.int64)]
    fmt = compute_format(data_size=2, ptrs_size=0, fields=fields)
    assert fmt == 'ixxxxq'


def test_primitive():
    fields = [field.Primitive(0, Types.int64),
              field.Primitive(8, Types.int64)]
    ctor = structor('ctor', data_size=2, ptrs_size=0, fields=fields)
    buf = ctor(FakeBlob, 1, 2)
    assert buf == ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
                   '\x02\x00\x00\x00\x00\x00\x00\x00') # 2


def test_void():
    fields = [field.Primitive(0, Types.int64),
              field.Primitive(8, Types.int64),
              field.Void()]
    ctor = structor('ctor', data_size=2, ptrs_size=0, fields=fields)
    buf = ctor(FakeBlob, 1, 2)
    assert buf == ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
                   '\x02\x00\x00\x00\x00\x00\x00\x00') # 2

def test_string():
    fields = [field.Primitive(0, Types.int64),
              field.String(8)]
    ctor = structor('ctor', data_size=1, ptrs_size=1, fields=fields)
    buf = ctor(FakeBlob, 1, 'hello capnp')
    assert buf == ('\x01\x00\x00\x00\x00\x00\x00\x00'
                   '\x01\x00\x00\x00\x62\x00\x00\x00'
                   'h' 'e' 'l' 'l' 'o' ' ' 'c' 'a'
                   'p' 'n' 'p' '\x00\x00\x00\x00\x00')

def test_struct():
    class MyStruct(Blob):
        __data_size__ = 2
        __ptrs_size__ = 0

    mybuf = ('\x01\x00\x00\x00\x00\x00\x00\x00'
             '\x02\x00\x00\x00\x00\x00\x00\x00')
    mystruct = MyStruct.from_buffer(mybuf, 0, None)
    #
    fields = [field.Struct(0, MyStruct)]
    ctor = structor('ctor', data_size=0, ptrs_size=1, fields=fields)
    buf = ctor(FakeBlob, mystruct)
    assert buf == ('\x00\x00\x00\x00\x02\x00\x00\x00'  # ptr to mystruct
                   + mybuf)


def test_list():
    fields = [field.List(0, Types.int8)]
    ctor = structor('ctor', data_size=0, ptrs_size=1, fields=fields)
    buf = ctor(FakeBlob, [1, 2, 3, 4])
    assert buf == ('\x01\x00\x00\x00\x22\x00\x00\x00'   # ptrlist
                   '\x01\x02\x03\x04\x00\x00\x00\x00')  # 1,2,3,4 + padding
