all:
	python setup.py build_ext --inplace

clean:
	find capnpy '(' -name '*.c' -or -name '*.so' ')' -print -delete
	rm -rf build dist

schema:
	python -m capnpy compile capnpy/schema.capnp --no-pyx --no-convert-case
	python -m capnpy compile capnpy/annotate.capnp --no-pyx --no-convert-case
