#include "baseblob.h"

PyTypeObject BaseBlobType;


static void BaseBlob_dealloc(BaseBlobObject *self) {
    Py_XDECREF(self->buf);
    Py_XDECREF(self->segment_offsets);
    self->ob_type->tp_free((PyObject*)self);
}


static int
BaseBlob_init(BaseBlobObject *self, PyObject *args, PyObject *kwds)
{
    PyErr_Format(PyExc_NotImplementedError, "Cannot instantiate Blob directly; "
                 "use Blob.from_buffer instead");
    return -1;
}

static PyObject *
BaseBlob_from_buffer(PyTypeObject *cls, PyObject *args, PyObject *kwds)
{
    BaseBlobObject *self;
    static char *kwlist[] = {"buf", "offset", "segment_offsets", NULL};

    self = (BaseBlobObject*)PyType_GenericNew(cls, args, kwds);
    if (self == NULL)
        return NULL;

    if (!PyObject_TypeCheck(self, &BaseBlobType)) {
        PyErr_Format(PyExc_TypeError, "expected a BaseBlob subclass");
        return NULL;
    }

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OiO", kwlist, 
                                     &self->buf, &self->offset,
                                     &self->segment_offsets))
        return NULL;

    Py_INCREF(self->buf);
    Py_INCREF(self->segment_offsets);
    return (PyObject*)self;
}


static PyMemberDef BaseBlob_members[] = {
    {"_buf", T_OBJECT_EX, offsetof(BaseBlobObject, buf), 0,
     "_buf"},
    {"_offset", T_INT, offsetof(BaseBlobObject, offset), 0,
     "offset"},
    {"_segment_offsets", T_OBJECT_EX, offsetof(BaseBlobObject, segment_offsets), 0,
     "_segment_offsets"},
    {NULL}  /* Sentinel */
};


static PyMethodDef BaseBlob_methods[] = {
    {"from_buffer", (PyCFunction)BaseBlob_from_buffer, 
     METH_VARARGS | METH_KEYWORDS | METH_CLASS,
     NULL},

    {NULL}  /* Sentinel */
};


PyTypeObject BaseBlobType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "capnpy.speedups.BaseBlob",/*tp_name*/
    sizeof(BaseBlobObject),    /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)BaseBlob_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,        /*tp_flags*/
    "BaseBlob",                   /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    BaseBlob_methods,             /* tp_methods */
    BaseBlob_members,             /* tp_members */
    0,           /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)BaseBlob_init,      /* tp_init */
    0,                         /* tp_alloc */
    0,                         /* tp_new */
};
