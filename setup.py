from distutils.core import setup, Extension

speedups_ext = Extension("capnpy.speedups",
                         ["capnpy/speedups/speedups.c",
                          "capnpy/speedups/baseblob.c",
                          "capnpy/speedups/primitive_field.c"])

setup(name="capnpy", version="0.0",
      ext_modules = [speedups_ext])
