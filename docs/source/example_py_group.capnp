# WARNING: the docs use literalinclude with :lines: to show only parts of this
# file. If you modify it, make sure that the :lines: are still correct!
@0x97a960ad8d4cf616;
using Py = import "/capnpy/annotate.capnp";

struct Point {
    x @0 :Int64;
    y @1 :Int64;
    color @2 :Text;
    position @3 :Void $Py.group("x, y") $Py.key("*");
}
