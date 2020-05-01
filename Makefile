all:
	python2.7 setup.py build_ext --inplace
	python3.7 setup.py build_ext --inplace
	python3.8 setup.py build_ext --inplace

x:
	python2.7 -m pytest capnpy/testing/test__hash.py -x
	python3.7 -m pytest capnpy/testing/test__hash.py -x
	python3.8 -m pytest capnpy/testing/test__hash.py -x

clean:
	find capnpy '(' -name '*.c' -or -name '*.so' ')' -and -not -name '_hash_cpython.c' -print -delete
	rm -rf build dist

annotate:
	python3.8 -m capnpy compile capnpy/annotate.capnp --no-pyx --no-version-check --no-reflection

schema: annotate
	python3.8 -m capnpy compile capnpy/schema.capnp --no-pyx --no-convert-case --no-version-check --no-reflection

# run only python2 and python3 tests: this should good enough to be checked
# locally before pushing and run the whole tests on travis
test:
	tox -e py27-test,py36-test,py37-test,py38-test
