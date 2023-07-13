#!/bin/bash
set -e -x

# Compile wheels
PYTHONS=(
    cp27-cp27m
    cp27-cp27mu
    cp35-cp35m
    cp36-cp36m
    cp37-cp37m
    cp38-cp38
    )

for pydir in "${PYTHONS[@]}"; do
    pybin=/opt/python/$pydir/bin
    "${pybin}/pip" install 'cython>=0.29.30'
    "${pybin}/pip" wheel /capnpy/ -w wheelhouse/

    # workaround for this bug:
    # https://github.com/pypa/pip/issues/8165#issuecomment-624669107
    rm -rf /capnpy/build

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
