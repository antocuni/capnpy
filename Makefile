all:
	python setup.py build_ext --inplace

clean:
	find capnpy '(' -name '*.c' -or -name '*.so' ')' -print -delete
	rm -rf build dist

annotate:
	python -m capnpy compile capnpy/annotate.capnp --no-pyx --no-version-check

schema: annotate
	python -m capnpy compile capnpy/schema.capnp --no-pyx --no-convert-case --no-version-check

# run only python2 and python3 tests: this should good enough to be checked
# locally before pushing and run the whole tests on travis
test:
	tox -e py27-test,py36-test
