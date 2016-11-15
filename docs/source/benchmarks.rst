===========
Benchmarks
===========

This is an example of benchmark


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


.. benchmark:: Get Attribute
   :foreach: b.python_implementation
   :filter: b.group == 'getattr'
   :series: b.params.schema
   :group:  b.extra_info.attribute_type


.. benchmark:: Union special attributes
   :foreach: b.python_implementation
   :filter: b.group == 'getattr_special' or b.name == 'test_numeric[Capnpy-int16]'
   :series: 'Capnpy'
   :group:  get_group(b)

   def get_group(b):
       name = charter.extract_test_name(b.name)
       if name == 'numeric':
           return 'int16'
       return name


.. benchmark:: Hashing
   :foreach: b.python_implementation
   :filter: b.group.startswith('hash')
   :series: b.extra_info.schema
   :group:  b.extra_info.type


.. benchmark:: Constructors
   :foreach: b.python_implementation
   :filter: b.group == 'ctor'
   :series: b.params.schema
   :group:  charter.extract_test_name(b.name)


.. benchmark:: Loading messages
   :foreach: b.python_implementation
   :filter: b.group == 'load'
   :series: b.params.schema
   :group:  charter.extract_test_name(b.name)


.. benchmark:: Buffered streams
   :foreach: b.python_implementation
   :filter: b.group == 'buffered'
   :series: None
   :group:  charter.extract_test_name(b.name)

