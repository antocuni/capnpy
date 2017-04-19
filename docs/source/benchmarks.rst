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
``group`` and ``struct``, and getting the length of a ``list``.

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


Lists
======

These benchmark measure the time taken to perform various operations on
lists. The difference with the ``list`` benchmark of the previous section is
that here we do not take into account the time taken to **read** the list
itself out of its containing struct, but only the time taken to perform the
operations after we got it.

The ``iter`` benchmark iterates over a list of 4 elements.

.. benchmark:: List
   :foreach: b.python_implementation
   :filter: b.group == 'list'
   :series: b.params.schema
   :group:  charter.extract_test_name(b.name)



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
buffer. However, as the following charts show, creating new ``capnpy`` objects
is almost as fast as creating instances. As shown by the charts, the
performances are different depending on the type of the fields of the target
struct.

List fields are special: normally, if you pass a list object to an instance or
namedtuple, you store only a reference to it. However, if you need to
construct a new Cap'n Proto object, you need to copy the whole content of the
list into the new buffer. In particular, if it is a list of structs, you need
to deeep-copy each item of the list, separately. This explains why
``test_list`` looks slower than the rest.

.. benchmark:: Constructors
   :foreach: b.python_implementation
   :filter: b.group == 'ctor'
   :series: b.params.schema
   :group:  charter.extract_test_name(b.name)


Deep copy
==========

Sometimes we need to perform a deep-copy of a Cap'n Proto object. In
particular, this is needed:

  - if you construct a new object having a struct field

  - if you construct a new object having a list of structs field

  - if you ``dump()`` an object which is not "compact"

``capnpy`` includes a generic, schema-less implementation which can
recursively copy an arbritrary Capn'n Proto pointer into a new buffer. It is
written in pure Python but compiled with Cython, and heavily optimized for
speed. ``PyCapnp`` relies on the official capnproto implementation written in
C++.

The ``copy_pointer`` benchmarks repeatedly copies a big recursive tree so that
the majority of the time is spent inside the deep-copy function and we can
ignore the small amout of time spent outside. Thus, we are effetively
benchmarking our Cython-based function against the heavily optimized C++
one. The resulting speed is very good. On some machine, it has measured to be
even **faster** than the C++ version.

.. benchmark:: Deep copy
   :foreach: b.python_implementation
   :filter: b.group == 'copy_pointer'
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


Dumping messages
================

These benchmark measure the performance of dumping an existing ``capnpy``
object into a message to be sent over the wire. At mimimum, to dump a message
you need to copy all the bytes which belongs to the object: this is measured
by ``test_copy_buffer``, which blindly copy the entire buffer and it is used
as a baseline.

The actual implementation of ``dumps()`` needs to do more: in particular, it
needs to compute the exact range of bytes to copy. Thus, the goal is that
``dumps()`` should be as close as possible to ``copy_buffer``.

If the structure was inside a ``capnpy`` list, it will be "non compact": in
other words, it is not represented by a contiguous amount of bytes in
memory. In that case, ``dumps()`` needs to do even more work to produce the
message. At the moment of writing, the implementation of ``.compact()`` is
known to be slow and non-optimized.

.. benchmark:: Dumps
   :foreach: b.python_implementation
   :filter: b.group == 'dumps'
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
   :filter: b.group == 'getattr' and b.name == 'test_list[Capnpy]' and b.python_implementation != 'PyPy'
   :series: b.extra_info.attribute_type

.. benchmark:: Special union attributes
   :timeline:
   :foreach: b.python_implementation
   :filter: b.group == 'getattr_special' and b.params.schema == 'Capnpy'
   :series: charter.extract_test_name(b.name)

.. benchmark:: List
   :timeline:
   :foreach: b.python_implementation
   :filter: b.group == 'list' and b.params.schema == 'Capnpy'
   :series: charter.extract_test_name(b.name)

.. benchmark:: Hashing
   :timeline:
   :foreach: b.python_implementation
   :filter: b.group.startswith('hash') and b.extra_info.schema == 'Capnpy'
   :series: b.extra_info.type

.. benchmark:: Constructors
   :timeline:
   :foreach: b.python_implementation
   :filter: b.group == 'ctor' and b.params.schema == 'Capnpy'
   :series: charter.extract_test_name(b.name)

.. benchmark:: Deep-copy
   :timeline:
   :foreach: b.python_implementation
   :filter: b.group == 'copy_pointer' and b.params.schema == 'Capnpy'
   :series: charter.extract_test_name(b.name)

.. benchmark:: Loading messages
   :timeline:
   :foreach: b.python_implementation
   :filter: b.group == 'load' and b.params.schema == 'Capnpy'
   :series: charter.extract_test_name(b.name)

.. benchmark:: Buffered streams
   :timeline:
   :foreach: b.python_implementation
   :filter: b.group == 'buffered' and 'makefile' not in b.name
   :series: charter.extract_test_name(b.name)

.. benchmark:: Dumping messages
   :timeline:
   :foreach: b.python_implementation
   :filter: b.group == 'dumps'
   :series: charter.extract_test_name(b.name)

