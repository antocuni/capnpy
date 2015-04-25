Structs
-------

capnp structs are composed of three parts:

  - data: area of buffer containing non-pointer values

  - ptrs: area of buffer containing pointers

  - extra: area of buffer containing the objects referred by ptrs

For the purpose of this document, we consider objects which fit into a single
capnp segment, i.e. we do not consider "far pointers".

"data" and "ptrs" are always contiguous: we call it the "body". Pointers are
encoded as offsets from the current word. In general, the objects in "extra"
can be anywhere and in any order (each box represent an arbitrary amount of
words)::


    +------------+  <----------------------+
    |    data    |                         |
    +------------+  <----------+           |
    |  ptr to A  |             |      body |
    +------------+        ptrs |           |
    |  ptr to B  |             |           |
    +------------+  <----------+-----------+
    |  garbage   |
    +------------+  <----------+
    |            |             |
    .            .             |
    .     B      .             |
    .            .             |
    |            |             |
    +------------+             |
    |  garbage   |       extra |
    +------------+             |
    |            |             |
    .            .             |
    .     A      .             |
    .            .             |
    |            |             |
    +------------+  <----------+


Note that A and B are also structs, and thus they follow the same layout,
recursively.

Note also that for each struct type, the size of the body is always fixed,
while the size of extra might vary (e.g. if it contains strings or lists).

With "garbage", we refer to any sequence of bytes which don't belong to the
struct in question. It might simply be unused, or it might contain objects
pointed by other structs (thus, what is "garbage" from the point of view of
struct X, might not be garbage from the point of view of struct Y).

Normal form
-----------

XXX: how does it compare to "canonical form"? It seems to be pretty similar,
but I need to check the details

A struct is "normalized", or in "normal form", if it holds the following
properties:

  1) The objects inside "extra" are laid out in the same order as the pointers
     referring to them. In other words, the offsets in the ptrs section must
     be strictly monotone, with the exception of NULL pointers (whose offset
     is always 0).

  2) There must be no garbage between the end of an object inside "extra" and
     the start of the next one. Note that it's still possible to have garbage
     between the end of the body and the beginning of the extra. This is
     necessary to implement lists, as we will see later.

Thus, the previous struct in normal form looks like this::

    +------------+  <----------+
    |    data    |             |
    +------------+             |
    |  ptr to A  |        body |
    +------------+             |
    |  ptr to B  |             |
    +------------+  <----------+
    |  garbage   |
    +------------+  <----------+
    |   A body   |             |
    +------------+             |
    |  garbage   |             |
    +------------+             |
    |  A extra   |             |
    +------------+       extra |
    |   B body   |             |
    +------------+             |
    |  garbage   |             |
    +------------+             |
    |  B extra   |             |
    +------------+  <----------+


Lists
-----

Normalized lists are laid out like this::

    +------------+
    | TAG (opt.) |
    +------------+
    |  #1 body   |
    +------------+  <----------+
    |  #2 body   |             |
    +------------+  <--------------------------+
    .            .             |               |
    .            .  #1 garbage |               |
    .            .             |               |
    +------------+             |    #2 garbage |
    |  #n body   |             |               |
    +------------+  <----------+               |
    |  #1 extra  |                             |
    +------------+  <--------------------------+
    |  #2 extra  |
    +------------+
    .            .
    .            .
    .            .
    +------------+
    |  #n extra  |
    +------------+

capnp requires that the item bodies are put consecutively: this is needed to
allow fast indexing into the list, because the item n is located at the offset
n*sizeof(data+ptrs).

As you can see from the diagram, the "garbage" of each list item is made of
the other list items which are in between. That's why we need to allow garbage
between the body and the extra section of an arbitrary struct.

Note that, by construction, there cannot be any garbage between "#n body" and
#1 extra" (XXX: is it correct? I THINK so, but I'm not fully convinced)


Nested lists
---------------

Nested lists contain pointers as items, and are compact by construction::

    +-----------------+
    |    TAG (opt.)   |
    +-----------------+
    |  ptr to list[0] |
    +-----------------+
    |  ptr to list[1] |
    +-----------------+
    |  ptr to list[2] |
    +-----------------+
    |    list[0][0]   |
    +-----------------+
    |    list[0][1]   |
    +-----------------+
    |    list[1][0]   |
    +-----------------+
    |    list[1][1]   |
    +-----------------+
    |    list[2][0]   |
    +-----------------+




Equality
--------

The big advantage of using a normalized layout is that it allow for efficient
comparison for equality between objects: it is enough to compare byte-by-byte
the body sections and the extra sections.

It is NOT possible to compare the sections lexicographically byte-by-byte.

The proof is left as an excercise to the reader :)


Compute the extra size
----------------------

To get the start of the extra section, it is sufficient to dereference the
first pointer in the ptrs section.

To get the end of the extra section:

  1) dereference the last pointer

  2) if the referenced object has no more pointers, the extra section ends at
     the end of it

  3) if the referenced object has pointers, dereference the last one and go
     back to point 1.

