#!/bin/bash
set -e

CAPNPROTO=capnproto-c++-0.7.0

if [ ! -d "$CAPNPROTO" ]; then
    echo 'Compiling capnproto'
    curl -O https://capnproto.org/$CAPNPROTO.tar.gz
    tar zxf $CAPNPROTO.tar.gz
    cd $CAPNPROTO
    ./configure
    make -j3
else
    echo 'Using cached capnproto'
    cd $CAPNPROTO
fi

sudo make install
capnp --version
