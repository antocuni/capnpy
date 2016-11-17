@0xe1f94ddddf8858c4;
struct Person {
  name @0 :Text;
  job :union {
      unemployed @1 :Void;
      employer @2 :Text; # this is the company name
      selfEmployed @3 :Void;
  }
}
