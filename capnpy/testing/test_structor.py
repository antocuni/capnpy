from capnpy.blob import Blob
from capnpy.structor import structor, compute_format
from capnpy import field
from capnpy.type import Types

class FakeBlob(object):

    @classmethod
    def from_buffer(cls, buf, offset, segment_offsets):
        return buf



def test_compute_format_simple():
    fields = [field.Primitive('x', 0, Types.int64),
              field.Primitive('y', 8, Types.int64)]
    fmt = compute_format(data_size=2, ptrs_size=0, fields=fields)
    assert fmt == 'qq'

def test_compute_format_holes():
    fields = [field.Primitive('x', 0, Types.int32),
              field.Primitive('y', 8, Types.int64)]
    fmt = compute_format(data_size=2, ptrs_size=0, fields=fields)
    assert fmt == 'ixxxxq'


def test_primitive():
    fields = [field.Primitive('x', 0, Types.int64),
              field.Primitive('y', 8, Types.int64)]
    ctor = structor('ctor', data_size=2, ptrs_size=0, fields=fields)
    buf = ctor(FakeBlob, 1, 2)
    assert buf == ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
                   '\x02\x00\x00\x00\x00\x00\x00\x00') # 2

def test_argnames():
    fields = [field.Primitive('x', 0, Types.int64),
              field.Primitive('y', 8, Types.int64)]
    ctor = structor('ctor', data_size=2, ptrs_size=0, fields=fields)
    buf = ctor(FakeBlob, y=2, x=1)
    assert buf == ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
                   '\x02\x00\x00\x00\x00\x00\x00\x00') # 2

def test_unordered():
    fields = [field.Primitive('y', 8, Types.int64),
              field.Primitive('x', 0, Types.int64)]
    ctor = structor('ctor', data_size=2, ptrs_size=0, fields=fields)
    buf = ctor(FakeBlob, x=1, y=2)
    assert buf == ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
                   '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
    buf = ctor(FakeBlob, 2, 1) # y must come first
    assert buf == ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
                   '\x02\x00\x00\x00\x00\x00\x00\x00') # 2


def test_void():
    fields = [field.Primitive('x', 0, Types.int64),
              field.Primitive('y', 8, Types.int64),
              field.Void('z')]
    ctor = structor('ctor', data_size=2, ptrs_size=0, fields=fields)
    buf = ctor(FakeBlob, 1, 2)
    assert buf == ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
                   '\x02\x00\x00\x00\x00\x00\x00\x00') # 2

def test_string():
    fields = [field.Primitive('x', 0, Types.int64),
              field.String('y', 8)]
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
    fields = [field.Struct('x', 0, MyStruct)]
    ctor = structor('ctor', data_size=0, ptrs_size=1, fields=fields)
    buf = ctor(FakeBlob, mystruct)
    assert buf == ('\x00\x00\x00\x00\x02\x00\x00\x00'  # ptr to mystruct
                   + mybuf)


def test_list():
    fields = [field.List('x', 0, Types.int8)]
    ctor = structor('ctor', data_size=0, ptrs_size=1, fields=fields)
    buf = ctor(FakeBlob, [1, 2, 3, 4])
    assert buf == ('\x01\x00\x00\x00\x22\x00\x00\x00'   # ptrlist
                   '\x01\x02\x03\x04\x00\x00\x00\x00')  # 1,2,3,4 + padding

def test_tag_offset():
    ## struct Shape {
    ##   area @0 :Int64;
    ##   union {
    ##     circle @1 :Int64;      # radius
    ##     square @2 :Int64;      # width
    ##   }
    ## }
    #
    fields = [field.Primitive('area', 0, Types.int64),
              field.Primitive('square', 8, Types.int64)]
    new_square = structor('new_square', data_size=3, ptrs_size=0,
                          fields=fields,
                          tag_offset=16, tag_value=1)
    buf = new_square(FakeBlob, area=64, square=8)
    assert buf == ('\x40\x00\x00\x00\x00\x00\x00\x00'     # area == 64
                   '\x08\x00\x00\x00\x00\x00\x00\x00'     # square == 8
                   '\x01\x00\x00\x00\x00\x00\x00\x00')    # which() == square, padding


def test_nullable():
    isnull = field.Primitive('isnull', 0, Types.int64)
    value = field.NullablePrimitive('value', 8, Types.int64, 0, isnull)
    fields = [isnull, value]
    ctor = structor('ctor', data_size=2, ptrs_size=0, fields=fields)
    buf = ctor(FakeBlob, value=42)
    assert buf == ('\x00\x00\x00\x00\x00\x00\x00\x00'  # NOT isnull
                   '\x2a\x00\x00\x00\x00\x00\x00\x00') # 42
    #
    buf = ctor(FakeBlob, value=None)
    assert buf == ('\x01\x00\x00\x00\x00\x00\x00\x00'  # isnull == 1
                   '\x00\x00\x00\x00\x00\x00\x00\x00') # 0
