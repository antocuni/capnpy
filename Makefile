all:
	python setup.py build_ext --inplace

clean:
	find capnpy '(' -name '*.c' -or -name '*.so' ')' -print -delete
	rm -rf build dist

schema:
	python -m capnpy compile capnpy/schema.capnp --no-pyx --no-convert-case --no-version-check
	python -m capnpy compile capnpy/annotate.capnp --no-pyx --no-convert-case --no-version-check
