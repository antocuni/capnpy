===========
Benchmarks
===========

Every time we push new code to github, our `Continuous Integration System`__
re-runs all the benchmarks and regenerates__ these charts.

__ https://travis-ci.org/antocuni/capnpy/
__ https://readthedocs.org/projects/capnpy/builds/

This section shows the current benchmark results and compares ``capnpy``
to various alternative implementations. `Evolution over time`_ shows how
``capnpy`` performance has evolved.

How to read the charts
=======================

For each benchmark we show two charts, one for CPython and one for
PyPy. Make sure to notice the different scale on the Y axis: PyPy is
often an order of magnitue faster than CPython, so it does not make sense
to directly compare them, but inside each chart it is useful to compare the
performance of ``capnpy`` to the other reference points.

Moreover, all benchmarks are written so that they repeat the same operation
for a certain number of iteration inside a loop. The charts show the total
time spent into the loop, not the time per iteration. Again, it is most useful
to just compare ``capnpy`` to the other reference points.

Most benchmarks compare the performance of ``capnpy`` objects against
alternative implementations. In particular:

:instance: objects are instances of plain Python classes. This is an useful
           reference point because often it represents the best we can
           potentially do. The goal of ``capnpy`` is to be as close as
           possible to instances.

:namedtuple: same as above, but using ``collections.namedtuple`` instead of
             Python classes.

:pycapnp_: the default Cap'n Proto implementation for Python. It does not work
           on PyPy.

.. _pycapnp: http://jparyani.github.io/pycapnp/


Get Attribute
=============

This benchmark measures how fast is to read an attribute out of an object, for
different types of attribute.

The benchmarks for ``group``, ``struct`` and ``list`` are expected to take a
bit longer than the others, because after getting the attribute, they "do
something" with the result, i.e. reading another attribute in case of
``group`` and ``struct``, and getting an item in case of ``list``.

At the time of writing, ``capnpy`` lists are terribly slow on CPython:
this is a known issue and will be fixed hopefully soon.

The PyPy charts shows that ``uint64`` fields are much slower than the others:
this is because the benchmarks are run on PyPy 5.4, which misses an
optimization in that area. With PyPy 5.6, ``uint64`` is as fast as ``int64``.


.. benchmark:: Get Attribute
   :foreach: b.python_implementation
   :filter: b.group == 'getattr'
   :series: b.params.schema
   :group:  b.extra_info.attribute_type


.. _special-union-attributes:

Special union attributes
=========================

If you have an :ref:`union`, you can inspect its tag value by calling
``which()``, ``__which__()`` or one of the ``is_*()`` methods. Ultimately, all
of them boil down to reading an ``int16`` field, so the corresponding
benchmark is included as a reference.

Note that on CPython, ``which()`` is slower than ``__which__()``: this is
because the former returns an :ref:`enum`, while the latter returns a raw
integer. On the other hand, PyPy is correctly able to optimize away all the
abstraction overhead.
            
.. benchmark:: Special union attributes
   :foreach: b.python_implementation
   :filter: b.group == 'getattr_special' or b.name == 'test_numeric[Capnpy-int16]'
   :series: 'Capnpy'
   :group:  get_group(b)

   def get_group(b):
       name = charter.extract_test_name(b.name)
       if name == 'numeric':
           return 'int16'
       return name


Hashing
========

If you use ``$Py.key`` (see :ref:`Equality and hashing`), you can ``hash``
your objects, and the return value is guaranteed to be the same as the
corresponding tuple.

The simplest implementation would be to create the tuple call ``hash()`` on
it.  However, ``capnpy`` uses an ad-hoc implementation so that it can compute
the hash value **without** creating the tuple. This is especially useful if
you have ``text`` fields, as you completely avoid the expensive creation of
the string.

.. benchmark:: Hashing
   :foreach: b.python_implementation
   :filter: b.group.startswith('hash')
   :series: b.extra_info.schema
   :group:  b.extra_info.type


Constructors
============

This benchmark measure the time needed to create new objects. Because of the
Cap'n Proto specs, this **has** to be more expensive than creating e.g. a new
instance, as we need to do extra checks and pack all the objects inside a
buffer.  However, we believe there is still room for improvement.

.. benchmark:: Constructors
   :foreach: b.python_implementation
   :filter: b.group == 'ctor'
   :series: b.params.schema
   :group:  charter.extract_test_name(b.name)


Loading messages
=================

These benchmark measure the performance of reading a stream of Cap'n Proto
messages, either from a file or from a TCP socket.

.. note:: ``pycapnp`` delegates the reading to the underlying C++ library, so
          you need to pass anything with a ``fileno()`` method: so, we pass a
          ``socket`` object directly.  On the other hand, ``capnpy`` needs a
          file-like object, so we pass a BufferedSocket__.

__ usage.html#loading-from-sockets

.. benchmark:: Loading messages
   :foreach: b.python_implementation
   :filter: b.group == 'load'
   :series: b.params.schema
   :group:  charter.extract_test_name(b.name)


.. _buffered-streams:

Buffered streams
================

As explained in the section :ref:`Loading from sockets`, ``capnpy`` provides
its own buffered wrapper around ``socket``, which is immensely faster than
``socket.makefile()``.

.. benchmark:: Buffered streams
   :foreach: b.python_implementation
   :filter: b.group == 'buffered'
   :series: None
   :group:  charter.extract_test_name(b.name)


Evolution over time
====================


.. benchmark:: Get Attribute
   :timeline:
   :foreach: b.python_implementation
   :filter: b.group == 'getattr' and \
            b.params.schema == 'Capnpy' and \
            (b.name != 'test_list[Capnpy]' or \
             b.python_implementation == 'PyPy')
   :series: b.extra_info.attribute_type

.. benchmark:: Get Attribute [CPython, list]
   :timeline:
   :filter: b.name == 'test_list[Capnpy]' and b.python_implementation != 'PyPy'
   :series: b.extra_info.attribute_type


