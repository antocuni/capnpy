from capnpy.builder import Builder
from capnpy.blob import Blob

def test_builder():
    builder = Builder(64)
    builder.allocate(24)
    builder.write_int64(0, 1)
    builder.write_int64(8, 2)
    builder.write_float64(16, 1.234)
    buf = builder.build()
    assert buf == ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
                   '\x02\x00\x00\x00\x00\x00\x00\x00'  # 2
                   '\x58\x39\xb4\xc8\x76\xbe\xf3\x3f') # 1.234

def test_write_struct():
    mybuf = ('\x01\x00\x00\x00\x00\x00\x00\x00'
             '\x02\x00\x00\x00\x00\x00\x00\x00')
    mystruct = Blob.from_buffer(mybuf, 0)
    builder = Builder(64)
    builder.allocate(8) # allocate enough space only for the pointer
    builder.write_struct(0, mystruct, data_size=16, ptrs_size=0)
    assert builder._size == 24 # 8 for the ptr, 16 for mystruct
    buf = builder.build()
    assert buf == ('\x00\x00\x00\x00\x02\x00\x00\x00'  # ptr to mystruct
                   + mybuf)
