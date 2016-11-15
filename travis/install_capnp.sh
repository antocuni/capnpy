#!/bin/bash
set -e

if [ ! -d "$HOME/capnp/lib" ]; then
    echo 'Compiling capnproto'
    curl -O https://capnproto.org/capnproto-c++-0.5.3.tar.gz
    tar zxf capnproto-c++-0.5.3.tar.gz
    cd capnproto-c++-0.5.3
    ./configure --prefix=$HOME/capnp
    make -j3
    make install
else
    echo 'Using cached directory.'
fi
