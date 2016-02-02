cdef extern from "Python.h":
    int PyObject_GenericSetAttr(object o, object attr_name, object v) except -1

cdef object SLOTS = set(
    ("__str__", "__repr__", "__getattribute__", "__getattr__",
     "__setattr__", "__delattr__", "__cmp__", "__repr__", "__hash__",
     "__call__", "__str__", "__getattribute__", "__getattr__", "__setattr__",
     "__delattr__", "__lt__", "__le__", "__eq__", "__ne__", "__gt__",
     "__ge__", "__iter__", "next", "__get__", "__set__", "__delete__",
     "__init__", "__new__", "__del__", "__add__", "__radd__", "__sub__",
     "__rsub__", "__mul__", "__rmul__", "__div__", "__rdiv__", "__mod__",
     "__rmod__", "__divmod__", "__rdivmod__", "__pow__", "__rpow__",
     "__neg__", "__pos__", "__abs__", "__nonzero__", "__invert__",
     "__lshift__", "__rlshift__", "__rshift__", "__rrshift__", "__and__",
     "__rand__", "__xor__", "__rxor__", "__or__", "__ror__", "__coerce__",
     "__int__", "__long__", "__float__", "__oct__", "__hex__", "__iadd__",
     "__isub__", "__imul__", "__idiv__", "__imod__", "__ipow__", "__ilshift__",
     "__irshift__", "__iand__", "__ixor__", "__ior__", "__floordiv__",
     "__rfloordiv__", "__truediv__", "__rtruediv__", "__ifloordiv__",
     "__itruediv__", "__index__", "__len__", "__getitem__", "__setitem__",
     "__delitem__", "__len__", "__add__", "__mul__", "__rmul__", "__getitem__",
     "__getslice__", "__setitem__", "__delitem__", "__setslice__",
     "__delslice__", "__contains__", "__iadd__", "__imul__"))


cpdef setattr_builtin(type o, object attr, object value):
    """
    Like settattr, but it works also on types defined in C (and in particular,
    in Cython), which you can't normally modify.

    Because of CPython's implementation details, it is not possible assign
    __special__ methods this way, so in that case a TypeError is raised
    """
    #
    # the function type_setattro, defined in typeobject.c, does three things:
    #   1. complain if the type is not an heap type
    #   2. set the attr by calling PyObject_GenericSetAttr
    #   3. update_slot(), which fixes things in case we set a special method
    #
    # The goal here is to bypass (1), so that we can set attrs also on Cython
    # types. However, there is no chance to call update_slot(), so we complain
    # in case we set e __special__ method. What is left is simply a call to
    # PyObject_GenericSetAttr, which modifies o->tp_dict.
    if attr in SLOTS:
        raise TypeError("Cannot set special methods on builtin types: %s" % attr)
    PyObject_GenericSetAttr(o, attr, value)

