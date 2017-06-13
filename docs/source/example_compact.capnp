@0xe62e66ea90a396da;
struct Point {
    x @0 :Int64;
    y @1 :Int64;
    name @2 :Text;
}

struct Polygon {
    points @0 :List(Point);
}