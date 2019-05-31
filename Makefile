all:
	python setup.py build_ext --inplace

clean:
	find capnpy '(' -name '*.c' -or -name '*.so' ')' -print -delete
	rm -rf build dist

annotate:
	python -m capnpy compile capnpy/annotate.capnp --no-pyx --no-version-check

schema: annotate
	python -m capnpy compile capnpy/schema.capnp --no-pyx --no-convert-case --no-version-check
