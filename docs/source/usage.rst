==================================
Usage
==================================

.. testsetup::

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
    print 'p2.x ==', p2.x
    print 'p2.y ==', p2.y

.. testoutput::

    p2.x == 1
    p2.y == 2


Loading schemas
================

``capnpy`` supports two different ways of loading schemas:

Dynamic loading
    to compile and load capnproto schemas on the fly.

Manual compilation
    to generate Python bindings for a schema, to be imported later.


If you use `dynamic loading`_, you always need the ``capnp`` executable
whenever you want to load a schema.

If you use `manual compilation`_, you need ``capnp`` to compile the schema, but
not to load it later; this means that you can distribute the precompiled
schemas, and the client machines will be able to load it without having to
install the official capnproto distribution.


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

``convert_case``
   If enabled, ``capnpy`` will automatically convert field names
   from camelCase to underscore_delimiter: i.e., ``fooBar`` will become
   ``foo_bar``. The default is **True**.


Dynamic loading
-----------------

To dynamically load a capnproto schema, use ``capnpy.load_schema``; its full
signature is::

    def load_schema(modname=None, importname=None, filename=None,
                    convert_case=True, pyx='auto'):
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

``pyx`` and ``convert_case`` specify which `compilation options`_ to use.


Manual compilation
-------------------

You can manually compile a capnproto schema by using ``python -m capnpy
compile``::

    $ python -m capnpy compile example.capnp

This will produce ``example.py`` (if you are using py mode) or ``example.so``
(if you are using pyx mode).


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


You can specify additional options by using ``capnpy_options``::

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
    >>> print p2.x, p2.y
    100 200

Alternatively, you can call ``load``/``loads`` directly on the class, and
``dump``/``dumps`` directly on the objects:

    >>> p = example.Point(x=100, y=200)
    >>> mybuf = p.dumps()
    >>> p2 = example.Point.loads(mybuf)
    >>> print p2.x, p2.y
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

capnproto types
================

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

Named unions
-------------

Named unions are a special case of groups.

.. literalinclude:: example_union.capnp
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
   :emphasize-lines: 5
   :lines: 13-17

.. doctest::

    >>> OlderPoint = mod.OlderPoint
    >>> p1 = OlderPoint(1, 2) # there is no "name" yet

Then, you receive some other object created with a newer schema which contains
an additional field, such as our ``Point``. Since ``Point`` is an evolution of
``OlderPoint``, it is perfectly lecit to load it:

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
    >>> print p.distance()
    5.0


``capnpy`` vs ``pycapnp``
==========================

To be written
