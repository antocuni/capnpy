#include "Python.h"
#include "structmember.h"
#include "baseblob.h"

extern PyTypeObject BaseBlobType; // defined in baseblob.c

typedef struct {
    PyObject_HEAD
    PyObject *name;
    long offset;
    PyObject *type;
    char fmt;
} PrimitiveFieldObject;

static void PrimitiveField_dealloc(PrimitiveFieldObject *self) {
    Py_XDECREF(self->name);
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
PrimitiveField_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PrimitiveFieldObject *self;

    self = (PrimitiveFieldObject *)type->tp_alloc(type, 0);
    if (self == NULL)
        return NULL;
    Py_INCREF(Py_None);
    self->name = Py_None;
    self->offset = 0;
    Py_INCREF(Py_None);
    self->type = Py_None;
    self->fmt = '\0';
    return (PyObject *)self;
}

static char get_fmt(PyObject *fmt)
{
    return 'q'; // XXX
}


static int
PrimitiveField_init(PrimitiveFieldObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"name", "offset", "type", NULL};
    PyObject *name=NULL, *type=NULL;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OiO", kwlist, 
                                     &name, &self->offset, &type))
        return -1;
    
    if (name) {
        Py_XDECREF(self->name);
        Py_INCREF(name);
        self->name = name;
    }

    if (type) {
        Py_XDECREF(self->type);
        Py_INCREF(type);
        self->type = type;
        PyObject *fmt = PyObject_GetAttrString(type, "fmt");
        self->fmt = get_fmt(fmt);
        if (self->fmt == '\0')
            return -1;
    }

    return 0;
}

static PyMemberDef PrimitiveField_members[] = {
    {"name", T_OBJECT_EX, offsetof(PrimitiveFieldObject, name), 0,
     "name"},
    {"offset", T_INT, offsetof(PrimitiveFieldObject, offset), 0,
     "offset"},
    {"type", T_OBJECT_EX, offsetof(PrimitiveFieldObject, type), 0,
     "type"},
    {NULL}  /* Sentinel */
};


static PyObject *
PrimitiveField_descr_get(PrimitiveFieldObject *self, PyObject *obj, PyObject *type)
{
    if (obj == NULL || obj == Py_None) {
        Py_INCREF(self);
        return (PyObject*)self;
    }

    if (!PyObject_TypeCheck(obj, &BaseBlobType)) {
        PyErr_Format(PyExc_TypeError, "expected a capnpy.speedups.BaseBlob instance");
        return NULL;
    }

    BaseBlobObject *blob = (BaseBlobObject*)obj;

    char* mybuf = PyString_AsString(blob->buf);
    char* valueaddr = mybuf + blob->offset + self->offset;
    long value = *((long*)valueaddr);
    return Py_BuildValue("i", value);
}


PyTypeObject PrimitiveFieldType = {
    PyObject_HEAD_INIT(NULL)
    0,                                  /*ob_size*/
    "capnpy.speedups.PrimitiveField",   /*tp_name*/
    sizeof(PrimitiveFieldObject),       /*tp_basicsize*/
    0,                                  /*tp_itemsize*/
    (destructor)PrimitiveField_dealloc, /*tp_dealloc*/
    0,                                  /*tp_print*/
    0,                                  /*tp_getattr*/
    0,                                  /*tp_setattr*/
    0,                                  /*tp_compare*/
    0,                                  /*tp_repr*/
    0,                                  /*tp_as_number*/
    0,                                  /*tp_as_sequence*/
    0,                                  /*tp_as_mapping*/
    0,                                  /*tp_hash */
    0,                                  /*tp_call*/
    0,                                  /*tp_str*/
    0,                                  /*tp_getattro*/
    0,                                  /*tp_setattro*/
    0,                                  /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,                 /*tp_flags*/
    "PrimitiveField",                   /* tp_doc */
    0,                                  /* tp_traverse */
    0,                                  /* tp_clear */
    0,                                  /* tp_richcompare */
    0,                                  /* tp_weaklistoffset */
    0,                                  /* tp_iter */
    0,                                  /* tp_iternext */
    NULL,                               /* tp_methods */
    PrimitiveField_members,             /* tp_members */
    NULL,                               /* tp_getset */
    0,                                  /* tp_base */
    0,                                  /* tp_dict */
    (descrgetfunc)PrimitiveField_descr_get,           /* tp_descr_get */
    0,                                  /* tp_descr_set */
    0,                                  /* tp_dictoffset */
    (initproc)PrimitiveField_init,      /* tp_init */
    0,                                  /* tp_alloc */
    PrimitiveField_new,                 /* tp_new */
};
