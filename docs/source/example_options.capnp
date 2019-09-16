@0x97a960ad8d4cf616;
using Py = import "/capnpy/annotate.capnp";

# don't convert the case by default
$Py.options(convertCase=false);

struct A {
    fieldOne @0 :Int64;
}

struct B $Py.options(convertCase=true) {
    fieldOne @0 :Int64;
    fieldTwo @1 :Int64;
    fieldThree @2 :Int64 $Py.options(convertCase=false);
}
