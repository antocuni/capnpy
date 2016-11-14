===========
Benchmarks
===========

This is an example of benchmark

.. benchmark:: Get Attribute
   :filter: b.group == 'getattr'
   :series: b.params.schema
   :group:  b.extra_info.attribute_type

.. benchmark:: Union special attributes
   :filter: b.group == 'getattr_special' or b.name == 'test_numeric[Capnpy-int16]'
   :series: 'Capnpy'
   :group:  get_group(b)

   def get_group(b):
       name = generator.extract_test_name(b.name)
       if name == 'numeric':
           return 'int16'
       return name
