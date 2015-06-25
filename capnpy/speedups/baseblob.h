#include "Python.h"
#include "structmember.h"

typedef struct {
    PyObject_HEAD
    PyObject *buf;
    long offset;
    PyObject *segment_offsets;
} BaseBlobObject;

extern PyTypeObject BaseBlobType;
