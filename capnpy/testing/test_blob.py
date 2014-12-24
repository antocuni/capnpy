import py
from capnpy.blob import Blob, Types
from capnpy.enum import enum

def test_Blob():
    # buf is an array of int64 == [1, 2]
    buf = ('\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
           '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
    b1 = Blob.from_buffer(buf, 0)
    assert b1._read_primitive(0, Types.Int64) == 1
    assert b1._read_primitive(8, Types.Int64) == 2
    #
    b2 = Blob.from_buffer(buf, 8)
    assert b2._read_primitive(0, Types.Int64) == 2

def test_Blob_ctor():
    py.test.raises(NotImplementedError, "Blob()")
    

def test_float64():
    buf = '\x58\x39\xb4\xc8\x76\xbe\xf3\x3f'   # 1.234
    blob = Blob.from_buffer(buf, 0)
    assert blob._read_primitive(0, Types.Float64) == 1.234

def test_deref_ptrstruct():
    buf = '\x90\x01\x00\x00\x02\x00\x04\x00'
    blob = Blob.from_buffer(buf, 0)
    offset = blob._deref_ptrstruct(0)
    assert offset == 808


def test_read_struct():
    ## struct Point {
    ##   x @0 :Int64;
    ##   y @1 :Int64;
    ## }
    buf = ('\x00\x00\x00\x00\x02\x00\x00\x00'    # ptr to {x, y}
           '\x01\x00\x00\x00\x00\x00\x00\x00'    # x == 1
           '\x02\x00\x00\x00\x00\x00\x00\x00')   # y == 2
    blob = Blob.from_buffer(buf, 0)
    p = blob._read_struct(0, Blob)
    assert p._buf is blob._buf
    assert p._offset == 8
    assert p._read_primitive(0, Types.Int64) == 1
    assert p._read_primitive(8, Types.Int64) == 2

def test_nested_struct():
    ## struct Rectangle {
    ##   a @0 :Point;
    ##   b @1 :Point;
    ## }
    buf = ('\x04\x00\x00\x00\x02\x00\x00\x00'    # ptr to a
           '\x08\x00\x00\x00\x02\x00\x00\x00'    # ptr to b
           '\x01\x00\x00\x00\x00\x00\x00\x00'    # a.x == 1
           '\x02\x00\x00\x00\x00\x00\x00\x00'    # a.y == 2
           '\x03\x00\x00\x00\x00\x00\x00\x00'    # b.x == 3
           '\x04\x00\x00\x00\x00\x00\x00\x00')   # b.y == 4
    rect = Blob.from_buffer(buf, 0)
    p1 = rect._read_struct(0, Blob)
    p2 = rect._read_struct(8, Blob)
    assert p1._read_primitive(0, Types.Int64) == 1
    assert p1._read_primitive(8, Types.Int64) == 2
    assert p2._read_primitive(0, Types.Int64) == 3
    assert p2._read_primitive(8, Types.Int64) == 4
    

def test_null_pointers():
    buf = '\x00\x00\x00\x00\x00\x00\x00\x00'    # NULL pointer
    blob = Blob.from_buffer(buf, 0)
    assert blob._read_struct(0, Blob) is None
    assert blob._read_list(0, None, None) is None
    assert blob._read_string(0) is None


def test_union():
    ## struct Shape {
    ##   area @0 :Int64;
    ##   union {
    ##     circle @1 :Int64;      # radius
    ##     square @2 :Int64;      # width
    ##   }
    ## }
    class Shape(Blob):
        __union_tag_offset__ = 16
        __union_tag__ = enum('Shape.__union_tag__', ('circle', 'square'))
    
    buf = ('\x40\x00\x00\x00\x00\x00\x00\x00'     # area == 64
           '\x08\x00\x00\x00\x00\x00\x00\x00'     # square == 8
           '\x01\x00\x00\x00\x00\x00\x00\x00')    # which() == square, padding

    shape = Shape.from_buffer(buf, 0)
    assert shape.which() == Shape.__union_tag__.square
