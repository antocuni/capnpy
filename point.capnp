@0x81c4687b4625b527;

struct Point {
  x @0 :Int64;
  y @1 :Int64;
}

struct Rectangle {
  a @0 :Point;
  b @1 :Point;
}

struct Polygon {
  points @0 :List(Point);
}