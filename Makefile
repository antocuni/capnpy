all:
	python setup.py build_ext --inplace

clean:
	find capnpy '(' -name '*.c' -or -name '*.so' ')' -print -delete

annotate:
	python -m capnpy compile capnpy/annotate.capnp --no-pyx

schema: annotate
	python -m capnpy compile capnpy/schema.capnp --no-pyx --no-convert-case
