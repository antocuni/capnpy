#!/bin/bash
set -e -x

# Compile wheels
PYTHONS=(
    cp27-cp27m
    cp27-cp27mu
    cp35-cp35m
    cp36-cp36m
    cp37-cp37m
    )

for pydir in "${PYTHONS[@]}"; do
    pybin=/opt/python/$pydir/bin
    "${pybin}/pip" install 'cython>=0.25'
    "${pybin}/pip" wheel /capnpy/ -w wheelhouse/

    # create the sdist if it does not exist yet
    if [[ ! -d /capnpy/dist ]]
    then
        (cd /capnpy && "${pybin}/python" setup.py sdist)
    fi
done

# Bundle external shared libraries into the wheels
for whl in wheelhouse/capnpy*.whl; do
    auditwheel repair "$whl" -w /capnpy/wheelhouse/
done
