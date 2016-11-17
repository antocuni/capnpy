# WARNING: the docs use literalinclude with :lines: to show only parts of this
# file. If you modify it, make sure that the :lines: are still correct!
@0xaff59c0b39ac4242;
using Py = import "/capnpy/annotate.capnp";

# the name will be ignored in comparisons, as it is NOT in the key
struct Point $Py.key("x, y") {
    x @0 :Int64;
    y @1 :Int64;
    name @2 :Text;
}

struct OlderPoint {
    x @0 :Int64;
    y @1 :Int64;
}
