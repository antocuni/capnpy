@0x8ced518a09aa7ce3;
struct Shape {
  area @0 :Float64;

  union {
    circle @1 :Float64;      # radius
    square @2 :Float64;      # width
  }
}
