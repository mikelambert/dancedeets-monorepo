#!/bin/bash

#TODO make PROCESSOR_COUNT dynamic
#built by docker.io, so reducing to 1. increase to match build server processor count as needed
export PROCESSOR_COUNT=1

export PYTHONUNBUFFERED=1

curl -L http://download.osgeo.org/geos/geos-3.5.0.tar.bz2 > geos.tar.bz2

mkdir geos
tar xf geos.tar.bz2 -C ./geos --strip-components=1

cd geos
./configure && make -j $PROCESSOR_COUNT && make install
ldconfig

cd ..
rm -rf geos
rm -rf geos.tar.bz2
