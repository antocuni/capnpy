#!/bin/bash
set -e

if [ ! -d "$HOME/capnp/lib" ]; then
    echo 'Compiling capnproto'
    CAPNPROTO=capnproto-c++-0.7.0
    curl -O https://capnproto.org/$CAPNPROTO.tar.gz
    tar zxf $CAPNPROTO.tar.gz
    cd $CAPNPROTO
    ./configure --prefix=$HOME/capnp
    make -j3
    make install
else
    echo 'Using cached capnproto'
fi
capnp --version
