all:
	python setup.py build_ext --inplace

clean:
	rm capnpy/*.c
	rm capnpy/*.so

schema:
	python -m capnpy compile capnpy/schema.capnp --no-pyx --no-convert-case
	python -m capnpy compile capnpy/annotate.capnp --no-pyx --no-convert-case
