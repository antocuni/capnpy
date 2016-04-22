=====================
capnpy Documentation
=====================

``capnpy`` is an implementation of Cap'n Proto for Python. Its primary goal is to
provide a library which is fast, both on CPython and PyPy, and which offers a
pythonic API and feeling whenever possible.

``capnpy`` supports two different ways of loading schemas:

  1. **Dynamic loading**: to compile load capnproto schemas on the fly

  2. **Precompiled mode**: to generate Python bindings for a schema, to be
     imported later (NOTE: this mode is not fully implemented as of now, but
     will be soon)

Moreover, it supports two different ways of compilation:

  1. **py mode**: generate pure Python modules, which can be used either on
     CPython or PyPy. This is optimized to be super fast on PyPy, but slowish
     on CPython, although it has the advantage of working with no extra setup
     (``capnpy`` itself uses ``schema.py``, a py-compiled version of
     ``schema.capnp``)

  2. **pyx mode**: generate pyx modules, which are then compiled into native
     extension modules by Cython and GCC. It is optimized for speed on CPython.


XXX explain how to enable cython support with setup.py

Quick example
-------------

Suppose to have a capnp schema called ``example.capnp`::

    @0xe62e66ea90a396da;
    struct Point {
        x @0 :Int64;
        y @1 :Int64;
    }

You can use ``capnpy`` to read and write messages of type ``Point``::

    import sys
    import capnpy
    example = capnpy.load_schema('example')
    #
    # read a message from the stdin
    p = capnpy.load(sys.stdin, example.Point)
    print p.x, p.y
    #
    # create a new capnp object and write it as a message
    p2 = example.Point(x=p.x+1, y=p.y+1)
    capnpy.dump(p2, sys.stdout)


Installation and requirements
------------------------------

``capnpy`` relies on the official capnproto implementation to parse the schema
files, so it needs to be able to find the ``capnp`` executable on the path
whenever you load or compile a schema.  This depends on the mode of operation;
in particular:

  1. for **dynamic loading**, you always need ``capnp`` to load a schema

  2. in **precompiled mode**, you need ``capnp`` to compile the schema, but not to
     load it later; this means that you can distribute the precompiled
     schemas, and the client machines will be able to load it without having
     to install the official capnproto distribution.


Dynamic loading
-----------------

To dynamically load a capnproto schema, use ``capnpy.load_schema``; its full
signature is::

    def load_schema(self, modname=None, importname=None, filename=None, convert_case=True):
        ...

``modname``, ``importname`` and ``filename`` corresponds to three different
ways to specify and locate the schema file to load. You need to pass exactly
one of them.

``modname`` (the default) is interpreted as if it were the name of a Python
module with the ``.capnp`` extension. This means that it is searched in all
the directories listed in ``sys.path`` and that you can use dotted names to
load a schema inside packages or subpackages::

    >>> import capnpy
    >>> import mypackage
    >>> mypackage
    <module 'mypackage' from '/tmp/mypackage/__init__.pyc'>
    >>> example = capnpy.load_schema('mypackage.mysub.example')
    >>> example
    <module 'example' from '/tmp/mypackage/mysub/example.capnp'>

This is handy because it allows you to distribute the capnproto schemas along
the Python packages, and to load them with no need to care where they are on
the filesystem, as long as the package is importable by Python.

``importname`` is similar to ``modname``, with the difference that it uses the
same syntax you would use in capnproto's *import expressions*. In particular,
if you use an absolute path, ``load_schema`` searches for the file in each of
the search path directories, which by default correspond to the ones listed in
``sys.path``. Thus, the example above is completely equivalent to this::

    >>> example = capnpy.load_schema(importname='/mypackage/mysub/example.capnp')
    >>> example
    <module 'example' from '/tmp/mypackage/mysub/example.capnp'>

Finally, ``filename`` specifies the exact file name of the schema file. No
search will be performed.

Additionally, you can also specify the ``convert_case`` parameter. By default,
``capnpy`` will translate names from **camelCase** to
**underscore_delimiter**; e.g., if the capnproto schema contains a field named
``personName``, the compiled Python module will contain a field named
``person_name``. You can disable this automatic translation by passing
``convert_case=False``.


Reading and writing messages
-----------------------------

The API to read and write capnproto messages is inspired by the ones offered
by ``pickle`` and ``json``:

  - ``capnpy.load(f, payload_type)``: load a message from a file-like object

  - ``capnpy.loads(s, payload)``: load a message from a string

  - ``capnpy.dumps(obj)``: write a message to a string

For example::

    >>> import capnpy
    >>> example = capnpy.load_schema('example')
    >>> p = example.Point(x=100, y=200)
    >>> mybuf = capnpy.dumps(p)
    >>> mybuf
    '\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00d\x00\x00\x00\x00\x00\x00\x00\xc8\x00\x00\x00\x00\x00\x00\x00'
    >>> p2 = capnpy.loads(mybuf, example.Point)
    >>> print p2.x, p2.y
    100 200

Alternatively, you can call ``load``/``loads`` directly on the class, and
``dump`` directly on the objects::

    >>> import capnpy
    >>> example = capnpy.load_schema('example')
    >>> p = example.Point(x=100, y=200)
    >>> mybuf = p.dumps()
    >>> mybuf
    '\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00d\x00\x00\x00\x00\x00\x00\x00\xc8\x00\x00\x00\x00\x00\x00\x00'
    >>> p2 = example.Point.loads(mybuf)
    >>> print p2.x, p2.y
    100 200


Struct
-------

``capnpy`` turns each capnproto struct into a Python class. The API is
inspired by ``namedtuples``:

  - the fields of the struct are exposed as plain attributes

  - objects are **immutable**; it is not possible to change the value of a
    field once the object has been instantiated. If you need to change the
    value of a field, you can instantiate a new object, as you would do with
    namedtuples

  - objects compares "by value": two objects are considered to be equal if
    their canonical form is the same. As a first approximation, this means
    that two objects are equal if all their fields are equal, as one would
    expect. See `this paragraph`_ for a more detailed explanation

  - objects are hashable, thus they can be used as keys of dictionaries, and
    they behave the way you would expect

Additionally, ``capnpy`` provides ways to access capnproto-specific features:

  - enums_

  - unions_


Enum
-----

capnproto enums are represented as subclasses of ``int``, so that we can
easily use both the numeric and the symbolic values::

    enum Color {
        red @0;
        green @1;
        blue @2;
        yellow @3;
    }

::

    >>> example = capnpy.load_schema('example')
    >>> Color = example.Color
    >>> Color.green
    <Color.green: 1>
    >>> int(Color.green)
    1
    >>> str(Color.green)
    'green'
    >>> Color.green + 2
    3
    >>> Color(2)
    <Color.blue: 2>
    >>> Color.__members__
    ('red', 'green', 'blue', 'yellow')


Union
------

capnproto uses a special enum value, called *tag*, to identify the field which
is currently set inside an union; ``capnpy`` follows this semantics by
automatically creating an enum whose members correspond to fields of the union::

    struct Shape {
      area @0 :Float64;

      union {
        circle @1 :Float64;      # radius
        square @2 :Float64;      # width
      }
    }

::

    >>> example = capnpy.load_schema('example')
    >>> Shape = example.Shape
    >>> Shape.__tag__
    <class 'capnpy.enum.Shape.__tag__'>
    >>> Shape.__tag__.__members__
    ('circle', 'square')

You can query which field is set by calling ``which()``, or by calling one of
the ``is_*()`` methods which are automatically generated::

    >>> s = capnpy.load(f, Shape)
    >>> s.which()
    <Shape.__tag__.circle: 0>
    >>> s.__which__()
    0
    >>> s.is_circle()
    True
    >>> s.is_square()
    False

The difference between ``which()`` and ``__which__()`` is that the former
return an ``Enum`` value, while the latter a raw integer: on CPython,
``which()`` is approximately 2x slower, so you might consider to use the raw
form in performance-critical parts of your code. On PyPy, the two forms have
the very same performance.

Since ``capnpy`` objects are immutable, union fields must be set when
instantiating the object. The first way is to call the default constructor and
set the field as usual::

    >>> s = Shape(area=16, square=4)
    >>> s.is_square()
    True

If you try to specify two conflicting fields, you get an error::

    >>> Shape(area=16, square=4, circle=5)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<0-codegen capnpy/compiler/__init__.py:145>", line 89, in __init__
        self._assert_undefined(square, "square", "circle")
      File "capnpy/struct_.py", line 70, in _assert_undefined
        (name, other_name))
    TypeError: got multiple values for the union tag: square, circle

The second way is to use one of the special ``new_*()`` alternate
constructors::

    >>> s = Shape.new_square(area=16, square=4)
    >>> s.is_square()
    True

    >>> s = Shape.new_square(area=16, square=4, circle=5)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: new_square() got an unexpected keyword argument 'circle'

The alternate constructors are especially handy in case of ``Void`` union
fields, because in that case you don't need to specify the (void) value of the
field::

    struct Type {
      union {
        void @0 :Void;
        bool @1 :Void;
        int64 @2 :Void;
        float64 @3 :Void;
        text @4 :Void;
      }
    }

::

    >>> t = Type.new_int64()
    >>> t.which()
    <Type.__tag__.int64: 2>
    >>> t.is_int64()
    True


Groups
------

Group fields are accessed using the usual dot notation::

    struct Point {
        position :group {
            x @0 :Int64;
            y @1 :Int64;
        }
        color @2 :Text;
    }

::

    >>> p = capnpy.load(f, Point)
    >>> p.position.x
    1
    >>> p.position.y
    2

When creating new objects, group fields are initialized using a tuple::

    >>> p2 = Point(position=(3, 4), 'red')
    >>> p2.position.x
    3
    >>> p2.position.y
    4

It is also possible to construct the tuple using keyword arguments, by using
an helper::

    >>> p3 = Point(position=Point.Position(x=5, y=6), color='red')
    >>> p3.position.x
    5
    >>> p3.position.y
    6

Note the difference between the lowercase ``Point.position`` which is used to
access the field, and the capitalized ``Point.Position`` which is used to
construct new objects.


More on equality
---------------------

XXX write me


Adding methods to capnproto structs
------------------------------------

As described above, each capnproto Struct is converted into a Python class,
whose attributes are specified by the capnproto schema. Moreover, with
``capnpy`` you can easily add methods to such classes.

To add methods, use the ``__extend__`` class decorator as shown here::

    >>> import math
    >>> import capnpy
    >>> example = capnpy.load_schema('example')
    >>> p = example.Point(x=3, y=4)
    >>> print p.distance()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    AttributeError: 'Point' object has no attribute 'distance'
    >>>
    >>> @example.Point.__extend__
    ... class Point:
    ...     def distance(self):
    ...         return math.sqrt(self.x**2 + self.y**2)
    ...
    >>> print p.distance()
    5.0

Although it seems magical, ``__extend__`` is much simpler than it looks: what
it does is simply to copy the content of the new class body ``Point`` into the
body of the automatically-generated ``example.Point``; the result is that
``example.Point`` contains both the original fields and the new methods; as
shown above, this affects also the objects created before the call to
``__extend__``.

When loading a schema, e.g. ``example.capnp``, ``capnpy`` also searches for a
file named ``example_extended.py`` in the same directory. If it exists, the
code is executed in the same namespace as the schema being loaded, meaning
that it is the perfect place where to put the ``__extend__`` code to be sure
that it will be immediately available. For example, suppose to have the
following ``example_extended.py`` in the same directory as ``example.capnp``::

    # example_extended.py
    import math
    @Point.__extend__
    class Point:
        def distance(self):
            return math.sqrt(self.x**2 + self.y**2)

Then, the ``distance`` method will be immediately available as soon as we load
the schema::

    >>> import capnpy
    >>> example = capnpy.load_schema('example')
    >>> p = example.Point(3, 4)
    >>> print p.distance()
    5.0


``capnpy`` vs ``pycapnp``
---------------------------

XXX write me
