#!/bin/bash

echo "Cloning benchmarks branch"
#set -v

REPO=`git config remote.origin.url`
BRANCH=benchmarks

rm .benchmarks -rf
git clone --depth=10 --branch=$BRANCH $REPO .benchmarks
