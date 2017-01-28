FROM gcr.io/dancedeets-hrd/gae-py-js

ENV PYTHONUNBUFFERED 1

#### Install GEOS ####
# Inspired by: https://hub.docker.com/r/cactusbone/postgres-postgis-sfcgal/~/dockerfile/

ENV GEOS http://download.osgeo.org/geos/geos-3.5.0.tar.bz2

#TODO make PROCESSOR_COUNT dynamic
#built by docker.io, so reducing to 1. increase to match build server processor count as needed
ENV PROCESSOR_COUNT 1

WORKDIR /install-postgis

WORKDIR /install-postgis/geos
ADD $GEOS /install-postgis/geos.tar.bz2
RUN tar xf /install-postgis/geos.tar.bz2 -C /install-postgis/geos --strip-components=1
RUN ./configure && make -j $PROCESSOR_COUNT && make install
RUN ldconfig
WORKDIR /install-postgis
RUN test -x geos
