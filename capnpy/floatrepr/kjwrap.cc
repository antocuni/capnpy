#include <string.h>
#include <kj/string.h>

extern "C" void capnpy_float32_repr(float x, char* buffer) {
    auto s = kj::str(x);
    const char* tmp = s.cStr();
    strcpy(buffer, tmp);
}

extern "C" void capnpy_float64_repr(double x, char* buffer) {
    auto s = kj::str(x);
    const char* tmp = s.cStr();
    strcpy(buffer, tmp);
}
