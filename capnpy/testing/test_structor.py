from capnpy.structor import Structor
from capnpy import field
from capnpy.type import Types

def test_simple():
    fields = [field.Primitive(0, Types.int64),
              field.Primitive(8, Types.int64)]
    ctor = Structor(data_size=2, ptrs_size=0, fields=fields)
    assert ctor.fmt == 'qq'

def test_holes():
    fields = [field.Primitive(0, Types.int32),
              field.Primitive(8, Types.int64)]
    ctor = Structor(data_size=2, ptrs_size=0, fields=fields)
    assert ctor.fmt == 'ixxxxq'


def test_call():
    fields = [field.Primitive(0, Types.int64),
              field.Primitive(8, Types.int64)]
    ctor = Structor(data_size=2, ptrs_size=0, fields=fields)
    buf = ctor(1, 2)
    assert buf == ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
                   '\x02\x00\x00\x00\x00\x00\x00\x00') # 2

