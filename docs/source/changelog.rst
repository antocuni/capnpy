==========
Changelog
==========

.. To see the commits between two versions:
   git log --graph --oneline 0.6.4..0.7.0

0.8.4
=====

* Change again the ``repr()`` of ``Data`` fields: it is not enough to escape
  non-ASCII chars, we need to escape non-printable chars as well.

0.8.3
=====

* Fix the ``repr()`` of ``Data`` fields when they contain non-ASCII characters

0.8.2
=====

* Add a Python2 fix so that calling ``repr()`` on structs does not crash in
  case fields contain non-ASCII characters

0.8.1
=====

* Fix the Reflection API in presence of large schemas, which ``capnp``
  compiles using multiple segments and far pointers.

0.8.0
=====

* Improve the ``shortrepr()`` method and consequently the ``__repr__`` of
  capnpy structs: the goal is to make the output of shortrepr() fully
  compatible with the standard ``capnp encode`` tool: this way it is possible
  to reconstruct the original binary message from a capnpy textual dump.

* Fix a corner case when reading far pointers: this bug prevented capnpy to
  parse large schemas under some conditions.

* Add a new compilation option to control whether to include the Reflection
  data: see :ref:`option`.

* Improve support for ``const`` inside capnproto schemas: it is now possible
  to declare struct and list constants.

0.7.0
=====

* Add the :ref:`Reflection API`, which makes it possible to programmatically
  query information about a schema, for example what are the fields inside a
  struct.

0.6.4
=====

* Fix ``$Py.groups`` collisions (`PR #45`_).

0.6.3
=====

* Fix the repr text fields when ``textType=unicode``.

0.6.2
=====

* Don't crash if we can't determine the version of ``capnp`` (`PR #43`_).


0.6.1
=====

* Improve ``load()`` and ``load_all()``. Try harder to distinguish between a
  clean close of the connection and an unclean one: now we raise EOFError
  *only* if we read an empty string at the very beginning of the message.

* Fix constructors when using a ``$Py.nullable`` on a group value.

0.6
====

* Add the new ``text_type`` option (see :ref:`option`). It is now possible to
  choose whether ``Text`` fields are represented as bytes or unicode.



.. _`PR #43`: https://github.com/antocuni/capnpy/pull/43
.. _`PR #45`: https://github.com/antocuni/capnpy/pull/45
