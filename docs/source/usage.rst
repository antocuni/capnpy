==================================
Usage
==================================

.. testsetup::

   from __future__ import print_function
   import sys
   import math
   # this is needed for capnpy.load_schema('example')
   sys.path.append('source')

Installation and requirements
=============================

To install ``capnpy``, just type::

  $ pip install capnpy

``capnpy`` relies on the official capnproto implementation to parse the schema
files, so it needs to be able to find the ``capnp`` executable to compile a
schema.  It requires ``capnp 0.5.0`` or later.


Quick example
=============

Suppose to have a capnp schema called ``example.capnp``:

.. literalinclude:: example.capnp
   :language: capnp

You can use ``capnpy`` to read and write messages of type ``Point``:

.. testcode::

    import capnpy
    # load the schema using dynamic loading
    example = capnpy.load_schema('example')
    # create a new Point object
    p = example.Point(x=1, y=2)
    # serialize the message and load it back
    message = p.dumps()
    p2 = example.Point.loads(message)
    print('p2.x ==', p2.x)
    print('p2.y ==', p2.y)

.. testoutput::

    p2.x == 1
    p2.y == 2


Compiling schemas
==================

``capnpy`` supports different ways of compiling schemas:

``setuptools`` integration
    to compile and distribute schemas using ``setup.py``.

Dynamic loading
    to compile and load capnproto schemas on the fly.

Manual compilation
    to compile schemas manually.


If you use ``setup.py`` or `manual compilation`_, you need ``capnp`` to
compile the schema, but not to load it later; this means that you can
distribute the precompiled schemas, and the client machines will be able to
load it without having to install the official capnproto distribution.

If you use `dynamic loading`_, you always need the ``capnp`` executable
whenever you want to load a schema.



Integration with ``setuptools``
--------------------------------

If you use ``setuptools``, you can use the ``capnpy_schema`` keyword to
automatically compile your schemas from ``setup.py``::

    from setuptools import setup
    setup(name='foo',
          version='0.1',
          packages=['mypkg'],
          capnpy_schemas=['mypkg/example.capnp'],
          )


You can specify additional `compilation options`_ by using ``capnpy_options``::

    from setuptools import setup
    setup(name='foo',
          version='0.1',
          packages=['mypkg'],
          capnpy_options={
              'pyx': False,          # do NOT use Cython (default is 'auto')
              'convert_case': False, # do NOT convert camelCase to camel_case
                                     # (default is True)
          }
          capnpy_schemas=['mypkg/example.capnp'],
          )


Manual compilation
-------------------

You can manually compile a capnproto schema by using ``python -m capnpy
compile``::

    $ python -m capnpy compile example.capnp

This will produce ``example.py`` (if you are using py mode) or ``example.so``
(if you are using pyx mode).  Run ``python -m capnpy --help`` for additional
options.


Dynamic loading
-----------------

To dynamically load a capnproto schema, use ``capnpy.load_schema``; its full
signature is::

    def load_schema(modname=None, importname=None, filename=None,
                    pyx='auto', options=None):
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

``pyx`` specifies whether to use pyx or py mode. ``options`` can be used to
change the default `compilation options`_:

.. doctest::

   >>> from capnpy.annotate import Options
   >>> example = capnpy.load_schema('example', options=Options(convert_case=False))

.. _option:

Compilation options
--------------------

The ``capnpy`` schema compiler has two modes of compilation:

py mode
   Generate pure Python modules, which can be used either on CPython or
   PyPy: it is optimized to be super fast on PyPy. It produces slow code on
   CPython, but it has the advantage of not requiring ``cython``. This is the
   default on PyPy.

pyx mode
   Generate pyx modules, which are then compiled into native extension
   modules by ``cython`` and ``gcc``. It is optimized for speed on
   CPython. This is the default on CPython, if ``cython`` is available.

Moreover, it supports the following options:

``version_check``
   If enabled, the compiled schema contains a check which is run at import
   time to ensure that the current version of capnpy matches to the one we
   compiled the schema with.  See note below for more details. The default is
   **True**.

``convert_case``
   If enabled, ``capnpy`` will automatically convert field names
   from camelCase to underscore_delimiter: i.e., ``fooBar`` will become
   ``foo_bar``. The default is **True**.

``text_type``
   Can be ``bytes`` or ``unicode``, Determines the default Python type for
   Text_ fields. The default is ``bytes``.

``include_reflection_data``
   If enabled, ``capnpy`` will embed `Reflection data`_ into the compiled
   schemas.

.. note:: **Version checking** is needed in particular if you are using pyx mode,
          which is the default on CPython.  Capnproto ``struct`` are
          represented by Python classes which inherits from
          ``capnpy.struct_.Struct``: in pyx mode, this is a Cython ``cdef
          class``, and it has a certain C layout which depends on the number
          and type of its fields. If the C layout at compilation and import
          time don't match, you risk segfault and/or misbehavior.  Since the
          internal layout of classes might change between capnpy version, the
          version check prevents this risk.


Options annotation
--------------------

``capnpy`` options can also be configured by using the ``$Py.options`` annotation,
which can be applied to ``file``, ``struct`` and ``field`` nodes.  The annotation
recurively applies also to all the children nodes and can be used to override
the options used by the parents.

This can be used to have a more granular control on how certain capnproto
types are translated into Python. For example, you could use it to apply the
``convert_case`` option only to certain structs or fields:

.. literalinclude:: example_options.capnp
   :language: capnp

.. doctest::

    >>> mod = capnpy.load_schema('example_options')
    >>> mod.A.fieldOne
    <property object at ...>
    >>> mod.B.field_one
    <property object at ...>
    >>> mod.B.field_two
    <property object at ...>
    >>> mod.B.fieldThree
    <property object at ...>

In the example above, ``A.fieldOne`` is not converted because of the
file-level annotation. ``B.field_one`` and ``B.field_two`` are converted
because the annotation on the struct overrides it. Finally, ``B.fieldThree``
overrides it again.

.. note:: Note the different spelling of options names: when you specify them
          in ``setup.py``, they follow Python's ``naming_convention`` and thus
          are spelled e.g. ``convert_case`` and ``text_type``. However, when
          you specify them as annotation, the capnproto schema language
          mandates ``camelCase``.


Loading and dumping messages
=============================

The API to read and write capnproto messages is inspired by the ones offered
by ``pickle`` and ``json``:

  - ``capnpy.load(f, payload_type)``: load a message from a file-like object

  - ``capnpy.loads(s, payload)``: load a message from a string

  - ``capnpy.load_all(f, payload_type)``: return a generator which yields all
    the messages from the given file-like object

  - ``capnpy.dump(obj)``: write a message to a file-like object

  - ``capnpy.dumps(obj)``: write a message to a string

For example:

    >>> import capnpy
    >>> example = capnpy.load_schema('example')
    >>> p = example.Point(x=100, y=200)
    >>> mybuf = capnpy.dumps(p)
    >>> mybuf
    '\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00d\x00\x00\x00\x00\x00\x00\x00\xc8\x00\x00\x00\x00\x00\x00\x00'
    >>> p2 = capnpy.loads(mybuf, example.Point)
    >>> print(p2.x, p2.y)
    100 200

Alternatively, you can call ``load``/``loads`` directly on the class, and
``dump``/``dumps`` directly on the objects:

    >>> p = example.Point(x=100, y=200)
    >>> mybuf = p.dumps()
    >>> p2 = example.Point.loads(mybuf)
    >>> print(p2.x, p2.y)
    100 200

By default, ``dump`` and ``dumps`` try to use a fast path which is faster if
you pass an object which is compact_. If the fast path can be taken, it is
approximately 5x faster on CPython and 10x faster on PyPy. However, if the
object is **not** compact, the fast path check makes it ~2x slower. If you are
sure that the object is not compact, you can disable the check by passing
``fastpath=False``:

    >>> mybuf = p.dumps(fastpath=False)


Loading from sockets
=====================

In case you want to load your messages from a ``socket``, you can use
``capnpy.buffered.BufferedSocket`` to wrap it into a file-like object::

  >>> from capnpy.buffered import BufferedSocket
  >>> sock = socket.create_connection(('localhost', 5000))
  >>> buf = BufferedSocket(sock)
  >>> example.Point.load(buf)

.. warning:: The obvious solution to wrap a socket into a file-like object
             would be to use ``socket.makefile()``. However, because of `this
             bug`__ it is horribly slow. **Don't use it**. See also the
             :ref:`benchmarks <buffered-streams>`.

__ https://bitbucket.org/pypy/pypy/issues/2272/socket_fileobjectread-horribly-slow


Raw dumps
=========

Raw dumps are intented primarly for debugging and should **never** be used as
a general transmission mechanism. They dump the internal state of the segments
and the offsets used to identify a given capnproto object.

In particular, they dump the whole buffer in which the object is contained,
which might be much larger that the object itself.

If you encounter a canpy bug, you can use ``_raw_dumps`` and ``_raw_loads`` to
save the offending object to make it easier to reproduce the bug:

    >>> p = example.Point(x=100, y=200)
    >>> mydump = p._raw_dumps()
    >>> p2 = example.Point._raw_loads(mydump)
    >>> print(p2.x, p2.y)
    100 200


capnproto types
================

Text
----

Capnproto defines ``Text`` fields as "always UTF-8 encoded and
NUL-terminated". There are at least two reasonable ways to represent this in
Python:

  - as ``bytes``: this will contain the undecoded UTF-8 string.

  - as ``unicode``: this will automatically do ``.decode('utf-8')`` for
    you. However, it is potentially less efficient because capnpy needs to
    re-decode the string again and again any time you read the field.

By default, ``Text`` fields are represented as ``bytes``. You can change the
default behavior by setting the appropriate `Compilation options`_. In case you
are using `Integration with setuptools`_, you need to pass
``capnpy_options={'text_type': 'unicode'}`` in your ``setup.py``.

If you want more granular control, you can annotate single files/struct/fields
by using the `Options annotation`_.


Struct
-------

``capnpy`` turns each capnproto struct into a Python class. The API is
inspired by ``namedtuples``:

  - the fields of the struct are exposed as plain attributes

  - objects are **immutable**; it is not possible to change the value of a
    field once the object has been instantiated. If you need to change the
    value of a field, you can instantiate a new object, as you would do with
    namedtuples

  - objects can be made `comparable and hashable`__ by specifying the
    ``$Py.key`` annotation

.. __: #equality-and-hashing


Moreover, in case the type of a field is a pointer (e.g. ``Text``, ``Data``,
structs and lists), ``capnpy`` generates two different accessors. For a field
named ``foo``:

  - ``has_foo()``: return ``True`` if ``foo`` is not ``NULL``, ``False``
    otherwise

  - ``get_foo()``: if ``has_foo()`` is ``True``, it is equivalent to
    ``foo``. Else, it returns the default value for that field

Note that in case of a ``struct`` field, the default value is a struct whose
fields have all the default value, recursively:

.. literalinclude:: example_struct.capnp
   :language: capnp

.. doctest::

    >>> mod = capnpy.load_schema('example_struct')
    >>> p = mod.Point()
    >>> p
    <Point: (x = 0, y = 0)>
    >>> print(p.name)
    None
    >>> p.has_name()
    False
    >>> p.get_name()
    ''
    >>> rect = mod.Rectangle()
    >>> print(rect.a)
    None
    >>> print(rect.has_a())
    False
    >>> print(rect.get_a())
    <Point: (x = 0, y = 0)>
    >>> rect.get_a().get_name()
    ''

The rationale is that ``get_foo()`` and ``has_foo()`` are modeled after the
semantics of the original C++ implementation of capnproto, while ``.foo`` is
modeled after the Pythonic ``namedtuple`` API. In particular ``.foo`` returns
``None`` instead of the default value to avoid unpythonic and surprising cases
such as ``Point(name=None).name == ''``

Enum
-----

capnproto enums are represented as subclasses of ``int``, so that we can
easily use both the numeric and the symbolic values:

.. literalinclude:: example_enum.capnp
   :language: capnp

.. doctest::

    >>> mod = capnpy.load_schema('example_enum')
    >>> Color = mod.Color
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
automatically creating an Enum_ whose members correspond to fields of the
union.

.. literalinclude:: example_union.capnp
   :language: capnp

.. doctest::

    >>> mod = capnpy.load_schema('example_union')
    >>> Shape, Type = mod.Shape, mod.Type
    >>> Shape.__tag__
    <class 'example_union.Shape__tag__'>
    >>> Shape.__tag__.__members__
    ('circle', 'square')
    >>> Type.__tag__.__members__
    ('void', 'bool', 'int64', 'float64', 'text')

You can query which field is set by calling ``which()``, or by calling one of
the ``is_*()`` methods which are automatically generated:

    >>> s = Shape(area=16, square=4)
    >>> s.which()
    <Shape__tag__.square: 1>
    >>> s.__which__()
    1
    >>> s.is_circle()
    False
    >>> s.is_square()
    True

The difference between ``which()`` and ``__which__()`` is that the former
return an ``Enum`` value, while the latter a raw integer: on CPython,
``which()`` is approximately :ref:`4x slower <special-union-attributes>`, so
you might consider to use the raw form in performance-critical parts of your
code. On PyPy, the two forms have the very same performance.

Since ``capnpy`` objects are immutable, union fields must be set when
instantiating the object. The first way is to call the default constructor and
set the field as usual:

    >>> s = Shape(area=3*3*math.pi, circle=3)
    >>> s.is_circle()
    True

If you try to specify two conflicting fields, you get an error:

    >>> Shape(area=16, square=4, circle=42)
    Traceback (most recent call last):
      ...
    TypeError: got multiple values for the union tag: circle, square

The second way is to use one of the special ``new_*()`` alternate
constructors:

    >>> s = Shape.new_square(area=16, square=4)
    >>> s.is_square()
    True

    >>> s = Shape.new_square(area=16, square=4, circle=42)
    Traceback (most recent call last):
      ...
    TypeError: new_square() got an unexpected keyword argument 'circle'

The alternate constructors are especially handy in case of ``Void`` union
fields, because in that case you don't need to specify the (void) value of the
field:

    >>> t = Type.new_int64()
    >>> t.which()
    <Type__tag__.int64: 2>
    >>> t.is_int64()
    True


Groups
------

.. literalinclude:: example_group.capnp
   :language: capnp

Group fields are initialized using a tuple, and accessed using the usual dot
notation:

    >>> mod = capnpy.load_schema('example_group')
    >>> Point = mod.Point
    >>> p = Point(position=(3, 4), color='red')
    >>> p.position.x
    3
    >>> p.position.y
    4

``capnpy`` also generates a **group constructor**, which is a ``staticmethod``
named as the capitalized group name. It is useful because you can use keyword
arguments and get the desired tuple in the right order:

    >>> Point.Position(y=6, x=5)
    (5, 6)
    >>> p2 = Point(position=Point.Position(x=5, y=6), color='red')
    >>> p2.position.x
    5
    >>> p2.position.y
    6

By using the group constructor, you can also **omit** some parameters; in this
case, they will get the default value, as usual:

    >>> Point.Position(y=7)
    (0, 7)

.. note:: Make sure to notice the difference between the lowercase
          ``Point.position`` which is a property used to read the field, and
          the capitalized ``Point.Position`` which is the group constructor:

          >>> Point.position
          <property object at ...>
          >>> Point.Position
          <function Position at ...>


Virtual groups
--------------

You can use the ``$Py.group`` annotation on a ``Void`` field to generate a
virtual group, which fishes the data from normal "flat" fields.

.. literalinclude:: example_py_group.capnp
   :language: capnp
   :emphasize-lines: 8
   :lines: 3-

This becomes particularly handy in conjuction with ``$Py.key`` (see `Equality
and hashing`_), because it allows to get an hashable/comparable subset of the
fields without affecting other parts of the code which want to access the
flat fields:

    >>> mod = capnpy.load_schema('example_py_group')
    >>> p = mod.Point(x=1, y=2, color='red')
    >>> p.x
    1
    >>> p.position.x
    1
    >>> p.position == (1, 2)
    True


Named unions
-------------

Named unions are a special case of groups.

.. literalinclude:: example_named_union.capnp
   :language: capnp


You can instantiate new objects as you would do with a normal group, by using
the group constructor. If you want to specify a ``Void`` union field, you can
use ``None``:

    >>> mod = capnpy.load_schema('example_named_union')
    >>> Person = mod.Person
    >>> p1 = Person(name='Alice', job=Person.Job(unemployed=None))
    >>> p2 = Person(name='Bob', job=Person.Job(employer='Capnpy corporation'))

Reading named unions is the same as anonymous ones:

    >>> p1.job.which()
    <Person_job__tag__.unemployed: 0>
    >>> p1.job.is_unemployed()
    True
    >>> p2.job.employer
    'Capnpy corporation'

.. note:: The reason why you have to use the group constructor is that it
          automatically insert the special ``undefined`` value in the right
          positions:

          >>> from capnpy.struct_ import undefined
          >>> undefined
          <undefined>
          >>> Person.Job(unemployed=None)
          (None, <undefined>, <undefined>)
          >>> Person.Job(employer='Capnpy corporation')
          (<undefined>, 'Capnpy corporation', <undefined>)


.. _compact:

"Compact" structs
==================

A struct object is said to be "compact" if:

  1. there is no gap between the data and pointers sections

  2. there is no gap between the children

  3. the pointers to the children are ordered

  4. the children are recursively compact

The compactness of a message depends on the implementation which generates it.
The most natural way to generate Cap'n Proto messages is to write them in
pre-order (i.e., you write first the root, then its children in order,
recursively). If the messages are generated this way and without introducing
gaps, it is automatically compact.

Messages created by ``capnpy`` are always compact.

You can check for compactness by calling the ``_is_compact`` method:

.. doctest::

    >>> mod = capnpy.load_schema('example_compact')
    >>> p = mod.Point(1, 2)
    >>> p._is_compact()
    True


List items
----------

Cap'n Proto lists are implemented in such a way that items are placed one next
to the other, and the children of the items are placed at the end of the list
body.  This means that, if the items have children, surely there will be a gap.

Hence, as soon as you have a Cap'n Proto list whose items have pointers, the
items are **not** compact, even if the list as a whole is.

.. doctest::

    >>> mod = capnpy.load_schema('example_compact')
    >>> p0 = mod.Point(1, 2, name='p0')
    >>> p1 = mod.Point(3, 4, name='p1')
    >>> poly = mod.Polygon(points=[p0, p1])
    >>> poly._is_compact()
    True
    >>> poly.points[0]._is_compact()
    False


The ``compact()`` method
-------------------------

Cap'n Proto message can be arbitrarly large and occupy a big amount of memory;
moreover, when you access a struct field or a list item, the resulting object
keeps alive the whole message.

However, sometimes you are interested in keeping alive only a smaller part it:
you can accomplish this by calling the ``compact()`` method, which creates a
new, smaller message containing only the desired subset. Also, as the name
suggests, the newly created message is guaranteed to be compact:

.. doctest::

    >>> mod = capnpy.load_schema('example_compact')
    >>> poly = mod.Polygon([mod.Point(1, 2, 'p0'), mod.Point(3, 4, 'p1')])
    >>> len(poly._seg.buf)
    80
    >>> p0 = poly.points[0]
    >>> len(p0._seg.buf)   # p0 keeps the whole segment alive
    80
    >>> p0._is_compact()
    False
    >>> pnew = p0.compact()
    >>> len(pnew._seg.buf) # pnew keeps only a subset alive
    40
    >>> pnew._is_compact()
    True


Equality and hashing
====================

By default, structs are not hashable and cannot be compared:

    >>> p1 = example.Point(x=1, y=2)
    >>> p2 = example.Point(x=1, y=2)
    >>> p1 == p2
    Traceback (most recent call last):
      ...
    TypeError: Cannot hash or compare capnpy structs. Use the $Py.key annotation to enable it

By specifying the ``$Py.key`` annotation, you explicitly tell ``capnpy`` which
fields to consider when doing equality testing and hashing:

.. literalinclude:: example_key.capnp
   :language: capnp
   :emphasize-lines: 5
   :lines: 3-12

.. doctest::

    >>> mod = capnpy.load_schema('example_key')
    >>> Point = mod.Point
    >>> p1 = Point(1, 2, "p1")
    >>> p2 = Point(1, 2, "p2")
    >>> p3 = Point(3, 4, "p3")
    >>>
    >>> p1 == p2
    True
    >>> p1 == p3
    False

You can also use them as dictionary keys:

    >>> d = {}
    >>> d[p1] = 'hello'
    >>> d[p2]
    'hello'

.. tip:: If you have many fields, you can use ``$Py.key("*")`` to include all
         of them in the comparison key: this is equivalent of explicitly
         listing all the fields which are present in the schema **at the
         moment of compilation**. In particular, be aware that if later get
         objects which come from a *newer* schema, the additional fields will
         **not** be considered in the comparisons.


Moreover, the structs are guaranteed to hash and compare equal to the
corresponding tuples:

    >>> p1 == (1, 2)
    True
    >>> p3 == (3, 4)
    True
    >>> d[(1, 2)]
    'hello'


Rationale
----------

Why are not structs comparable by defaults but you have to manually specify
``$Py.key``?  Couldn't ``capnpy`` be smart enough to figure out by itself?

We choose to use ``$Py.key`` because it is not obvious what is the right thing
to do in presence of schema evolution. For example, suppose you start with
previous version of ``struct Point`` which contains only ``x`` and ``y``:

.. literalinclude:: example_key.capnp
   :language: capnp
   :lines: 13-

.. doctest::

    >>> OlderPoint = mod.OlderPoint
    >>> p1 = OlderPoint(1, 2) # there is no "name" yet

Then, you receive some other object created with a newer schema which contains
an additional field, such as our ``Point``. Since ``Point`` is an evolution of
``OlderPoint``, it is perfectly legit to load it:

    >>> p_with_name = Point(1, 2, 'this is my name')
    >>> message_from_the_future = p_with_name.dumps()
    >>> p2 = OlderPoint.loads(message_from_the_future)
    >>> p2.x, p2.y
    (1, 2)

Now, note that the underyling data contains the name, although we don't have
the ``name`` field (because we are using an older schema):

    >>> hasattr(p2, 'name')
    False
    >>> 'this is my name' in p2._seg.buf
    True

So, what should ``p1 == p2`` return? We might choose to simply ignore the
``name`` and return ``True``. Or choose to consider ``p1.name`` equal to the
empty string, or to ``None``, and thus return ``False``. Or we could declare
that two objects are equal when their canonical representation is the same,
which introduces even more subtle consequences.

According to the Zen of Python:

    | *Explicit is better than implicit.*
    | *In the face of ambiguity, refuse the temptation to guess.*

Hence, we require you to explicity specify which fields to consider.


Extending ``capnpy`` structs
=============================

As described above, each capnproto ``struct`` is converted into a Python
class. With ``capnpy`` you can easily add methods by using the ``__extend__``
class decorator:

    >>> import math
    >>> import capnpy
    >>> Point = example.Point
    >>>
    >>> @Point.__extend__
    ... class Point:
    ...     def distance(self):
    ...         return math.sqrt(self.x**2 + self.y**2)
    ...
    >>>
    >>> p = Point(x=3, y=4)
    >>> p.distance()
    5.0

Although it seems magical, ``__extend__`` is much simpler than it looks: what
it does is simply to copy the content of the new class body ``Point`` into the
body of the automatically-generated ``example.Point``; the result is that
``example.Point`` contains both the original fields and the new methods.

When loading a schema, e.g. ``example.capnp``, ``capnpy`` also searches for a
file named ``example_extended.py`` in the same directory. If it exists, the
code is executed in the same namespace as the schema being loaded, meaning
that it is the perfect place where to put the ``__extend__`` code to be sure
that it will be immediately available. For example, suppose to have the
following ``example_extended.py`` in the same directory as ``example.capnp``::

    # example_extended.py
    import math

    # Note that the Point class is already available, as this code is executed
    # inside the namespace of the module loaded from example.capnp
    @Point.__extend__
    class Point:
        def distance(self):
            return math.sqrt(self.x**2 + self.y**2)

Then, the ``distance`` method will be immediately available as soon as we load
the schema:

    >>> import capnpy
    >>> example = capnpy.load_schema('example')
    >>> p = example.Point(3, 4)
    >>> print(p.distance())
    5.0


.. _`Reflection data`:

Reflection API
===============

Using the reflection API, it is possible to programmatically query information
about a schema, for example what are the fields inside a struct.

The main entry point is the function
``capnpy.get_reflection_data()``, which returns the metadata for a
given module as an instance of ``ReflectionData``.

.. doctest::

   >>> mod = capnpy.load_schema('example')
   >>> reflection = capnpy.get_reflection_data(mod)


Under the hood, the ``capnp`` compiler produces a `capnproto representation`_
of the parsed schema, where most capnproto entities are represented by
nodes_. You can use ``get_node`` to get the capnproto node corresponding to a
given Python-level entity:

.. doctest::

   >>> # get the node for the Point struct
   >>> node = reflection.get_node(mod.Point)
   >>> type(node)
   <class 'capnpy.schema.Node__Struct'>
   >>> node.displayName[-19:]
   'example.capnp:Point'
   >>> node.which()
   <Node__tag__.struct: 1>
   >>> node.is_struct()
   True
   >>> for f in node.struct.fields:
   ...     print(f)
   ...
   <Field 'x': int64>
   <Field 'y': int64>


.. note:: By default, reflection data is included into all compiled
          schemas. You can change the behavior by setting the option_
          ``include_reflection_data`` to ``False``.


.. _`capnproto representation`: https://github.com/antocuni/capnpy/blob/master/capnpy/schema.capnp
.. _nodes: https://github.com/antocuni/capnpy/blob/master/capnpy/schema.capnp#L30


Nodes vs Python entities
------------------------

When compiling a schema ``capnpy`` generates Python entities from nodes: for
example, ``Struct`` are compiled as Python classes, and fields as Python
properties. Although closely related, they are not always equivalent: for
example, ``Field.name`` is always ``camelCase``, but the Python property might
be called differently, depending on the `compilation options`_.

For example, consider the following schema:

.. literalinclude:: example_reflection.capnp
   :language: capnp

To get the correct Python-level name, you can call ``reflection.field_name()``:

.. doctest::

    >>> mod = capnpy.load_schema('example_reflection')
    >>> reflection = capnpy.get_reflection_data(mod)
    >>> node = reflection.get_node(mod.Foo)
    >>> f = node.get_struct_fields()[0]
    >>> f
    <Field 'myField': int64>
    >>> reflection.field_name(f)
    'my_field'

This works also for enums:

.. doctest::

    >>> node = reflection.get_node(mod.Color)
    >>> node.is_enum()
    True
    >>> enumerants = node.get_enum_enumerants()
    >>> enumerants[0].name
    'lightRed'
    >>> reflection.field_name(enumerants[0])
    'light_red'


Inspecting annotations
-----------------------

The Reflection API provides methods to inspect capnproto annotations. Consider
the following schema, in which we use custom annotations to map structs to
database tables:

.. literalinclude:: example_reflection_db.capnp
   :language: capnp


You can use ``has_annotation()`` and ``get_annotation()`` to query about them:

.. doctest::

    >>> mod = capnpy.load_schema('example_reflection_db')
    >>> reflection = capnpy.get_reflection_data(mod)
    >>> reflection.has_annotation(mod.Person, mod.dbTable)
    True
    >>> reflection.get_annotation(mod.Person, mod.dbTable)
    'Persons'

The following shows a complete example of how to use annotations to create a
simple dump of the DB structure.  It is also worth noticing the usage of
``reflection.field_name()`` to convert from e.g. ``firstName`` to
``first_name``:

.. doctest::

    >>> def print_table(node):
    ...     table = reflection.get_annotation(node, mod.dbTable)
    ...     print('DB Table:', table)
    ...     for f in node.get_struct_fields():
    ...         print('   ', reflection.field_name(f), end='')
    ...         if reflection.has_annotation(f, mod.dbPrimaryKey):
    ...             print(' PRIMARY KEY', end='')
    ...         print()
    >>>
    >>> for node in reflection.allnodes.values():
    ...     if reflection.has_annotation(node, mod.dbTable):
    ...         print_table(node)
    ...
    DB Table: Persons
        id PRIMARY KEY
        first_name
        last_name
        school
    DB Table: Schools
        id PRIMARY KEY
        name
        city


``capnpy`` vs ``pycapnp``
==========================

To be written
