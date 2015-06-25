#include "Python.h"
#include "structmember.h"

extern PyTypeObject BaseBlobType;
extern PyTypeObject PrimitiveFieldType;


PyMODINIT_FUNC
initspeedups(void)
{
    PyObject* m;

    BaseBlobType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&BaseBlobType) < 0)
        return;

    PrimitiveFieldType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&PrimitiveFieldType) < 0)
        return;

    m = Py_InitModule3("capnpy.speedups", NULL, "C speedups for capnpy");

    Py_INCREF(&PrimitiveFieldType);
    PyModule_AddObject(m, "PrimitiveField", (PyObject *)&PrimitiveFieldType);

    Py_INCREF(&BaseBlobType);
    PyModule_AddObject(m, "BaseBlob", (PyObject *)&BaseBlobType);

}
