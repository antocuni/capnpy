#!/bin/bash
set -e -x

# Compile wheels
PYTHONS=(
    cp27-cp27m
    cp27-cp27mu
    # cp35-cp35m
    # cp36-cp36m
    # cp37-cp37m
    # cp38-cp38
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

echo
echo "objdump ot capnpy/ptr.so"
pushd /tmp/
unzip /wheelhouse/testing_capnpy-0.0.1-cp27-cp27m-linux_x86_64.whl
objdump -T capnpy/ptr.so
popd


# Bundle external shared libraries into the wheels
for whl in wheelhouse/testing_capnpy*.whl; do
    auditwheel repair "$whl" -w /capnpy/wheelhouse/
done

echo
md5sum /capnpy/wheelhouse/*
