#!/bin/bash

# We use without-sandbox, so that we properly load all the modules/tests
nosetests --with-gae --without-sandbox --exclude="mapreduce|gdata|atom|httplib2|unittest2" $1 $2 $3 $4 $5

