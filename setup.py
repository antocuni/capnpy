from distutils.core import Extension
from setuptools import setup, find_packages


setup(name="capnpy",
      version="0.1",
      packages = find_packages(),
      package_data = {
          'capnpy': ['*.capnp']
          },
      ext_modules = [])
