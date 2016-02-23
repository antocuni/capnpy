import py
from capnpy.builder import StructBuilder
from capnpy.blob import Types
from capnpy.list import PrimitiveList, StructList, StringList
from capnpy.struct_ import Struct
from capnpy.printer import print_buffer

def test_primitive():
    builder = StructBuilder('qqd')
    buf = builder.build(1, 2, 1.234)
    assert buf == ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
                   '\x02\x00\x00\x00\x00\x00\x00\x00'  # 2
                   '\x58\x39\xb4\xc8\x76\xbe\xf3\x3f') # 1.234

def test_alloc_struct():
    class MyStruct(Struct):
        __static_data_size__ = 2
        __static_ptrs_size__ = 0

    mybuf = ('\x01\x00\x00\x00\x00\x00\x00\x00'
             '\x02\x00\x00\x00\x00\x00\x00\x00')
    mystruct = MyStruct.from_buffer(mybuf, 0, 2, 0)
    #
    builder = StructBuilder('q')
    ptr = builder.alloc_struct(0, MyStruct, mystruct)
    buf = builder.build(ptr)
    assert buf == ('\x00\x00\x00\x00\x02\x00\x00\x00'  # ptr to mystruct
                   + mybuf)


def test_alloc_struct_with_offset():
    class MyStruct(Struct):
        __static_data_size__ = 2
        __static_ptrs_size__ = 0

    mybuf = ('garbage0'
             '\x01\x00\x00\x00\x00\x00\x00\x00'
             '\x02\x00\x00\x00\x00\x00\x00\x00')
    mystruct = MyStruct.from_buffer(mybuf, 8, 2, 0)
    #
    builder = StructBuilder('q')
    ptr = builder.alloc_struct(0, MyStruct, mystruct)
    buf = builder.build(ptr)
    assert buf == ('\x00\x00\x00\x00\x02\x00\x00\x00'  # ptr to mystruct
                   + mybuf[8:])


def test_alloc_text():
    builder = StructBuilder('qq')
    ptr1 = builder.alloc_text(0, 'hello capnp')
    ptr2 = builder.alloc_text(8, 'hi world')
    buf = builder.build(ptr1, ptr2)
    expected_buf = ('\x05\x00\x00\x00\x62\x00\x00\x00'
                    '\x09\x00\x00\x00\x4a\x00\x00\x00'
                    'h' 'e' 'l' 'l' 'o' ' ' 'c' 'a'
                    'p' 'n' 'p' '\x00\x00\x00\x00\x00'
                    'h' 'i' ' ' 'w' 'o' 'r' 'l' 'd'
                    '\x00\x00\x00\x00\x00\x00\x00\x00')
    assert buf == expected_buf

def test_alloc_data():
    builder = StructBuilder('qq')
    ptr1 = builder.alloc_data(0, 'hello capnp')
    ptr2 = builder.alloc_data(8, 'hi world')
    buf = builder.build(ptr1, ptr2)
    expected_buf = ('\x05\x00\x00\x00\x5a\x00\x00\x00'
                    '\x09\x00\x00\x00\x42\x00\x00\x00'
                    'h' 'e' 'l' 'l' 'o' ' ' 'c' 'a'
                    'p' 'n' 'p' '\x00\x00\x00\x00\x00'
                    'h' 'i' ' ' 'w' 'o' 'r' 'l' 'd')
    assert buf == expected_buf


def test_alloc_list_int64():
    builder = StructBuilder('q')
    ptr = builder.alloc_list(0, PrimitiveList, Types.int64, [1, 2, 3, 4])
    buf = builder.build(ptr)
    assert buf == ('\x01\x00\x00\x00\x25\x00\x00\x00'   # ptrlist
                   '\x01\x00\x00\x00\x00\x00\x00\x00'   # 1
                   '\x02\x00\x00\x00\x00\x00\x00\x00'   # 2
                   '\x03\x00\x00\x00\x00\x00\x00\x00'   # 3
                   '\x04\x00\x00\x00\x00\x00\x00\x00')  # 4

def test_alloc_list_int8():
    builder = StructBuilder('q')
    ptr = builder.alloc_list(0, PrimitiveList, Types.int8, [1, 2, 3, 4])
    buf = builder.build(ptr)
    assert buf == ('\x01\x00\x00\x00\x22\x00\x00\x00'   # ptrlist
                   '\x01\x02\x03\x04\x00\x00\x00\x00')  # 1,2,3,4 + padding


def test_alloc_list_float64():
    builder = StructBuilder('q')
    ptr = builder.alloc_list(0, PrimitiveList, Types.float64,
                             [1.234, 2.345, 3.456, 4.567])
    buf = builder.build(ptr)
    assert buf == ('\x01\x00\x00\x00\x25\x00\x00\x00'   # ptrlist
                   '\x58\x39\xb4\xc8\x76\xbe\xf3\x3f'   # 1.234
                   '\xc3\xf5\x28\x5c\x8f\xc2\x02\x40'   # 2.345
                   '\xd9\xce\xf7\x53\xe3\xa5\x0b\x40'   # 3.456
                   '\xf8\x53\xe3\xa5\x9b\x44\x12\x40')  # 4.567

def test_alloc_list_of_structs():
    class Point(Struct):
        __static_data_size__ = 2
        __static_ptrs_size__ = 0

    buf1 = ('\x0a\x00\x00\x00\x00\x00\x00\x00'    # 10
            '\x64\x00\x00\x00\x00\x00\x00\x00')   # 100
    buf2 = ('\x14\x00\x00\x00\x00\x00\x00\x00'    # 20
            '\xc8\x00\x00\x00\x00\x00\x00\x00')   # 200
    buf3 = ('\x1e\x00\x00\x00\x00\x00\x00\x00'    # 30
            '\x2c\x01\x00\x00\x00\x00\x00\x00')   # 300
    buf4 = ('\x28\x00\x00\x00\x00\x00\x00\x00'    # 40
            '\x90\x01\x00\x00\x00\x00\x00\x00')   # 400
    p1 = Point.from_buffer(buf1, 0, 2, 0)
    p2 = Point.from_buffer(buf2, 0, 2, 0)
    p3 = Point.from_buffer(buf3, 0, 2, 0)
    p4 = Point.from_buffer(buf4, 0, 2, 0)
    #
    builder = StructBuilder('q')
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
    builder = StructBuilder('qqq')
    ptr1 = builder.alloc_struct(0, Struct, None)
    ptr2 = builder.alloc_text(8, None)
    ptr3 = builder.alloc_list(16, PrimitiveList, Types.int64, None)
    buf = builder.build(ptr1, ptr2, ptr3)
    assert buf == NULL*3

def test_alloc_list_of_strings():
    builder = StructBuilder('q')
    ptr = builder.alloc_list(0, StringList, None, ['A', 'BC', 'DEF', 'GHIJ'])
    buf = builder.build(ptr)
    expected_buf = ('\x01\x00\x00\x00\x26\x00\x00\x00'   # ptrlist
                    '\x0d\x00\x00\x00\x12\x00\x00\x00'   # ptr item 1
                    '\x0d\x00\x00\x00\x1a\x00\x00\x00'   # ptr item 2
                    '\x0d\x00\x00\x00\x22\x00\x00\x00'   # ptr item 3
                    '\x0d\x00\x00\x00\x2a\x00\x00\x00'   # ptr item 4
                    'A' '\x00\x00\x00\x00\x00\x00\x00'   # A
                    'B' 'C' '\x00\x00\x00\x00\x00\x00'   # BC
                    'D' 'E' 'F' '\x00\x00\x00\x00\x00'   # DEF
                    'G' 'H' 'I' 'J' '\x00\x00\x00\x00')  # GHIJ
    assert buf == expected_buf


def test_alloc_list_of_structs_with_pointers():
    class Person(Struct):
        __static_data_size__ = 1
        __static_ptrs_size__ = 1

    john =  ('\x20\x00\x00\x00\x00\x00\x00\x00'    # age=32
             '\x01\x00\x00\x00\x2a\x00\x00\x00'    # name=ptr
             'J' 'o' 'h' 'n' '\x00\x00\x00\x00')   # John

    # emily is a "split struct", with garbage between the body and the extra
    emily = ('garbage0'
             '\x18\x00\x00\x00\x00\x00\x00\x00'    # age=24
             '\x09\x00\x00\x00\x32\x00\x00\x00'    # name=ptr
             'garbage1'
             'garbage2'
             '\x45\x6d\x69\x6c\x79\x00\x00\x00'    # Emily
             'garbage3')

    john = Person.from_buffer(john, 0, 1, 1)
    emily = Person.from_buffer(emily, 8, 1, 1)
    #
    builder = StructBuilder('q')
    ptr = builder.alloc_list(0, StructList, Person, [john, emily])
    buf = builder.build(ptr)

    expected_buf = ('\x01\x00\x00\x00\x27\x00\x00\x00'    # ptrlist
                    '\x08\x00\x00\x00\x01\x00\x01\x00'    # list tag
                    '\x20\x00\x00\x00\x00\x00\x00\x00'    # age=32
                    '\x09\x00\x00\x00\x2a\x00\x00\x00'    # name=ptr
                    '\x18\x00\x00\x00\x00\x00\x00\x00'    # age=24
                    '\x05\x00\x00\x00\x32\x00\x00\x00'    # name=ptr
                    'J' 'o' 'h' 'n' '\x00\x00\x00\x00'    # John
                    'E' 'm' 'i' 'l' 'y' '\x00\x00\x00')   # Emily
    assert buf == expected_buf
