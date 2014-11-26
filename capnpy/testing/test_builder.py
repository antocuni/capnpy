from capnpy.builder import Builder

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
