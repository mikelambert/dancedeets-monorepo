#!/bin/bash

set -e

curl -L https://github.com/google/re2/archive/master.tar.gz | tar xvzf -
curl -L https://github.com/axiak/pyre2/archive/master.tar.gz | tar xvzf -

cd re2-master
make
make install
cd ..

cd pyre2-master
python setup.py build
python setup.py install
cd ..

rm -rf re2-master
rm -rf pyre2-master
