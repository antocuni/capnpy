import py
from pypytools.codegen import Code
from capnpy.struct_ import Struct
from capnpy.structor import Structor
from capnpy import field
from capnpy.type import Types

class FakeSlot(object):

    def __init__(self, offset, t):
        self.offset = offset
        self.t = t

    def get_fmt(self):
        return self.t.fmt

    def get_offset(self, data_size):
        return self.offset


class FakeType(object):

    def is_bool(self):
        return False

class FakeField(object):

    def __init__(self, name, offset, t):
        self.name = name
        self.slot = FakeSlot(offset, t)
        self.slot.type = FakeType()

    @classmethod
    def Void(cls, name):
        return cls(name, None, Types.void)

    def is_primitive(self):
        return self.slot.t.is_primitive()

    def is_slot(self):
        return True

    def is_group(self):
        return False

    def is_string(self):
        return False

    def is_void(self):
        return self.slot.t is Types.void

    def is_nullable(self, compiler):
        return False


class TestComputeFormat(object):

    def test_compute_format_simple(self):
        fields = [FakeField('x', 0, Types.int64),
                  FakeField('y', 8, Types.int64)]
        s = Structor(None, 'fake', data_size=2, ptrs_size=0, fields=fields)
        assert s.fmt == 'qq'

    def test_compute_format_holes(self):
        fields = [FakeField('x', 0, Types.int32),
                  FakeField('y', 8, Types.int64)]
        s = Structor(None, 'fake', data_size=2, ptrs_size=0, fields=fields)
        assert s.fmt == 'ixxxxq'


def new_structor(**kwds):
    class Namespace:
        from capnpy.builder import StructBuilder

    code = Code()
    code['__'] = Namespace
    structor = Structor(None, 'ctor', **kwds)
    structor.declare(code)
    code.compile()
    static_ctor = code['ctor']
    # the structor is defined as @staticmethod, so before calling we need to
    # manually __get__ it
    return static_ctor.__get__(object)




def test_unsupported(monkeypatch):
    monkeypatch.setattr(Structor, '_unsupported', 'fake')
    ctor = new_structor(data_size=0, ptrs_size=0, fields=[])
    exc = py.test.raises(NotImplementedError, "ctor()")
    assert exc.value.message == 'fake'

def test_primitive():
    fields = [FakeField('x', 0, Types.int64),
              FakeField('y', 8, Types.int64)]
    ctor = new_structor(data_size=2, ptrs_size=0, fields=fields)
    buf = ctor(1, 2)
    assert buf == ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
                   '\x02\x00\x00\x00\x00\x00\x00\x00') # 2

def test_argnames():
    fields = [FakeField('x', 0, Types.int64),
              FakeField('y', 8, Types.int64)]
    ctor = new_structor(data_size=2, ptrs_size=0, fields=fields)
    buf = ctor(y=2, x=1)
    assert buf == ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
                   '\x02\x00\x00\x00\x00\x00\x00\x00') # 2

def test_unordered():
    fields = [FakeField('y', 8, Types.int64),
              FakeField('x', 0, Types.int64)]
    ctor = new_structor(data_size=2, ptrs_size=0, fields=fields)
    buf = ctor(x=1, y=2)
    assert buf == ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
                   '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
    buf = ctor(2, 1) # y must come first
    assert buf == ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
                   '\x02\x00\x00\x00\x00\x00\x00\x00') # 2


def test_void():
    fields = [FakeField('x', 0, Types.int64),
              FakeField('y', 8, Types.int64),
              FakeField.Void('z')]
    ctor = new_structor(data_size=2, ptrs_size=0, fields=fields)
    buf = ctor(1, 2)
    assert buf == ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
                   '\x02\x00\x00\x00\x00\x00\x00\x00') # 2

@py.test.mark.xfail
def test_struct():
    class MyStruct(Struct):
        __data_size__ = 2
        __ptrs_size__ = 0

    mybuf = ('\x01\x00\x00\x00\x00\x00\x00\x00'
             '\x02\x00\x00\x00\x00\x00\x00\x00')
    mystruct = MyStruct.from_buffer(mybuf, 0, None)
    #
    fields = [field.Struct('x', 0, MyStruct)]
    ctor = new_structor(data_size=0, ptrs_size=1, fields=fields)
    buf = ctor(mystruct)
    assert buf == ('\x00\x00\x00\x00\x02\x00\x00\x00'  # ptr to mystruct
                   + mybuf)

@py.test.mark.xfail
def test_list():
    fields = [field.List('x', 0, Types.int8)]
    ctor = new_structor(data_size=0, ptrs_size=1, fields=fields)
    buf = ctor([1, 2, 3, 4])
    assert buf == ('\x01\x00\x00\x00\x22\x00\x00\x00'   # ptrlist
                   '\x01\x02\x03\x04\x00\x00\x00\x00')  # 1,2,3,4 + padding

@py.test.mark.xfail
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
    new_square = new_structor(data_size=3, ptrs_size=0,
                              fields=fields,
                              tag_offset=16, tag_value=1)
    buf = new_square(area=64, square=8)
    assert buf == ('\x40\x00\x00\x00\x00\x00\x00\x00'     # area == 64
                   '\x08\x00\x00\x00\x00\x00\x00\x00'     # square == 8
                   '\x01\x00\x00\x00\x00\x00\x00\x00')    # which() == square, padding


@py.test.mark.xfail
def test_nullable():
    isnull = field.Primitive('isnull', 0, Types.int64)
    value = field.NullablePrimitive('value', 8, Types.int64, 0, isnull)
    fields = [isnull, value]
    ctor = new_structor(data_size=2, ptrs_size=0, fields=fields)
    buf = ctor(value=42)
    assert buf == ('\x00\x00\x00\x00\x00\x00\x00\x00'  # NOT isnull
                   '\x2a\x00\x00\x00\x00\x00\x00\x00') # 42
    #
    buf = ctor(value=None)
    assert buf == ('\x01\x00\x00\x00\x00\x00\x00\x00'  # isnull == 1
                   '\x00\x00\x00\x00\x00\x00\x00\x00') # 0
