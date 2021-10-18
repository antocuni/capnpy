#!/bin/bash
set -e

# $CAPNPROTO is defined by test.yml env

if [ ! -d ~/capnproto ]; then
    echo 'Compiling capnproto'
    cd
    curl -O https://capnproto.org/$CAPNPROTO.tar.gz
    tar zxf $CAPNPROTO.tar.gz
    mv $CAPNPROTO capnproto
    cd capnproto
    ./configure
    make -j8
else
    echo 'Using cached capnproto'
    cd ~/capnproto
fi

sudo make install
capnp --version
