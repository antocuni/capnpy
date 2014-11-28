from capnpy.builder import Builder
from capnpy.blob import Blob, Types
from capnpy.list import PrimitiveList, StructList

def test_primitive():
    builder = Builder('qqd')
    buf = builder.build(1, 2, 1.234)
    assert buf == ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
                   '\x02\x00\x00\x00\x00\x00\x00\x00'  # 2
                   '\x58\x39\xb4\xc8\x76\xbe\xf3\x3f') # 1.234

def test_alloc_struct():
    class MyStruct(Blob):
        __data_size__ = 16
        __ptrs_size__ = 0

    mybuf = ('\x01\x00\x00\x00\x00\x00\x00\x00'
             '\x02\x00\x00\x00\x00\x00\x00\x00')
    mystruct = MyStruct.from_buffer(mybuf, 0)
    #
    builder = Builder('q')
    ptr = builder.alloc_struct(0, MyStruct, mystruct)
    buf = builder.build(ptr)
    assert buf == ('\x00\x00\x00\x00\x02\x00\x00\x00'  # ptr to mystruct
                   + mybuf)


def test_alloc_string():
    builder = Builder('qq')
    ptr1 = builder.alloc_string(0, 'hello capnproto')
    ptr2 = builder.alloc_string(8, 'hello world')
    buf = builder.build(ptr1, ptr2)
    assert buf == ('\x05\x00\x00\x00\x82\x00\x00\x00'
                   '\x09\x00\x00\x00\x62\x00\x00\x00'
                   'hello capnproto\0'
                   'hello world\0')
    assert False, 'This is wrong: we need to think about alignment'


def test_alloc_list_int64():
    builder = Builder('q')
    ptr = builder.alloc_list(0, PrimitiveList, Types.Int64, [1, 2, 3, 4])
    buf = builder.build(ptr)
    assert buf == ('\x01\x00\x00\x00\x25\x00\x00\x00'   # ptrlist
                   '\x01\x00\x00\x00\x00\x00\x00\x00'   # 1
                   '\x02\x00\x00\x00\x00\x00\x00\x00'   # 2
                   '\x03\x00\x00\x00\x00\x00\x00\x00'   # 3
                   '\x04\x00\x00\x00\x00\x00\x00\x00')  # 4

def test_alloc_list_float64():
    builder = Builder('q')
    ptr = builder.alloc_list(0, PrimitiveList, Types.Float64,
                             [1.234, 2.345, 3.456, 4.567])
    buf = builder.build(ptr)
    assert buf == ('\x01\x00\x00\x00\x25\x00\x00\x00'   # ptrlist
                   '\x58\x39\xb4\xc8\x76\xbe\xf3\x3f'   # 1.234
                   '\xc3\xf5\x28\x5c\x8f\xc2\x02\x40'   # 2.345
                   '\xd9\xce\xf7\x53\xe3\xa5\x0b\x40'   # 3.456
                   '\xf8\x53\xe3\xa5\x9b\x44\x12\x40')  # 4.567

def test_alloc_list_of_structs():
    class Point(Blob):
        __data_size__ = 16
        __ptrs_size__ = 0

    buf1 = ('\x0a\x00\x00\x00\x00\x00\x00\x00'    # 10
            '\x64\x00\x00\x00\x00\x00\x00\x00')   # 100
    buf2 = ('\x14\x00\x00\x00\x00\x00\x00\x00'    # 20
            '\xc8\x00\x00\x00\x00\x00\x00\x00')   # 200
    buf3 = ('\x1e\x00\x00\x00\x00\x00\x00\x00'    # 30
            '\x2c\x01\x00\x00\x00\x00\x00\x00')   # 300
    buf4 = ('\x28\x00\x00\x00\x00\x00\x00\x00'    # 40
            '\x90\x01\x00\x00\x00\x00\x00\x00')   # 400
    p1 = Point.from_buffer(buf1, 0)
    p2 = Point.from_buffer(buf2, 0)
    p3 = Point.from_buffer(buf3, 0)
    p4 = Point.from_buffer(buf4, 0)
    #
    builder = Builder('q')
    ptr = builder.alloc_list(0, StructList, Point, [p1, p2, p3, p4])
    buf = builder.build(ptr)
    expected_buf = ('\x01\x00\x00\x00\x47\x00\x00\x00'    # ptrlist
                    '\x10\x00\x00\x00\x02\x00\x00\x00'    # list tag
                    '\x0a\x00\x00\x00\x00\x00\x00\x00'    # 10
                    '\x64\x00\x00\x00\x00\x00\x00\x00'    # 100
                    '\x14\x00\x00\x00\x00\x00\x00\x00'    # 20
                    '\xc8\x00\x00\x00\x00\x00\x00\x00'    # 200
                    '\x1e\x00\x00\x00\x00\x00\x00\x00'    # 30
                    '\x2c\x01\x00\x00\x00\x00\x00\x00'    # 300
                    '\x28\x00\x00\x00\x00\x00\x00\x00'    # 40
                    '\x90\x01\x00\x00\x00\x00\x00\x00')   # 400
    assert buf == expected_buf

def test_null_pointers():
    NULL = '\x00\x00\x00\x00\x00\x00\x00\x00' # NULL pointer
    builder = Builder('qqq')
    ptr1 = builder.alloc_struct(0, Blob, None)
    ptr2 = builder.alloc_string(8, None)
    ptr3 = builder.alloc_list(16, PrimitiveList, Types.Int64, None)
    buf = builder.build(ptr1, ptr2, ptr3)
    assert buf == NULL*3
