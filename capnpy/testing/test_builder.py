from capnpy.builder import Builder
from capnpy.blob import Blob

def test_primitive():
    builder = Builder('qqd')
    buf = builder.build(1, 2, 1.234)
    assert buf == ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
                   '\x02\x00\x00\x00\x00\x00\x00\x00'  # 2
                   '\x58\x39\xb4\xc8\x76\xbe\xf3\x3f') # 1.234

def test_alloc_struct():
    mybuf = ('\x01\x00\x00\x00\x00\x00\x00\x00'
             '\x02\x00\x00\x00\x00\x00\x00\x00')
    mystruct = Blob.from_buffer(mybuf, 0)
    #
    builder = Builder('q')
    ptr = builder.alloc_struct(0, mystruct, Blob, data_size=16, ptrs_size=0)
    buf = builder.build(ptr)
    assert buf == ('\x00\x00\x00\x00\x02\x00\x00\x00'  # ptr to mystruct
                   + mybuf)


def test_alloc_string():
    builder = Builder('q')
    ptr = builder.alloc_string(0, 'hello capnproto')
    buf = builder.build(ptr)
    assert buf == ('\x01\x00\x00\x00\x82\x00\x00\x00'   # ptr
                   'hello capnproto\0')                 # string

