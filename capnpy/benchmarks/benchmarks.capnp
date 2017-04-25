@0xe62e66ea90a396da;

using Py = import "/capnpy/annotate.capnp";

enum Color {
    red @0;
    green @1;
    blue @2;
    yellow @3;
    pink @4;
}

struct MyStruct {
    # the padding field is needed to ensure that we benchmark fields with offset >0
    padding @0 :Int64;
    bool @1 :Int64; # XXX: should be Bool but it's not supported by structor
    int8 @2 :Int8;
    int16 @3 :Int16;
    int32 @4 :Int32;
    int64 @5 :Int64;
    uint8 @6 :UInt8;
    uint16 @7 :UInt16;
    uint32 @8 :UInt32;
    uint64 @9 :UInt64;
    float32 @10 :Float32;
    float64 @11 :Float64;
    text @12 :Text;
    group :group {
        field @13 :Int64;
    }
    inner @14 :MyInner;
    intlist @15 :List(Int64);
    color @16 :Color;
}

struct MyInner {
     field @0 :Int64;
}

struct WithUnion {
    padding @0 :Int64;
    union {
        zero @1  :Void;
        one @2   :Void;
        two @3   :Void;
        three @4 :Void;
    }
}

struct Point $Py.key("x, y, z") {
    x @0 :Int64;
    y @1 :Int64;
    z @2 :Int64;
}

struct StrPoint $Py.key("x, y, z") {
    x @0 :Text;
    y @1 :Text;
    z @2 :Text;
}

struct MyStructContainer {
    items @0 :List(MyStruct);
}

struct MyInt64List {
    items @0 :List(Int64);
}

struct Rectangle {
    a @0 :Point;
    b @1 :Point;
}


struct Node {
    x @0 :Int64;
    y @1 :Int64;
    z @2 :Int64;
    left @3 :Node;
    right @4 :Node;
}

struct Tree {
    root @0 :Node;
}
