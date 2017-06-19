#!/bin/bash
set -e -x

# Compile wheels
for PYBIN in /opt/python/cp27-*/bin; do
    "${PYBIN}/pip" install 'cython>=0.25'
    "${PYBIN}/pip" wheel /capnpy/ -w wheelhouse/

    # create the sdist if it does not exist yet
    if [[ ! -d /capnpy/dist ]]
    then
        (cd /capnpy && "${PYBIN}/python" setup.py sdist)
    fi
done

# Bundle external shared libraries into the wheels
for whl in wheelhouse/capnpy*.whl; do
    auditwheel repair "$whl" -w /capnpy/wheelhouse/
done
