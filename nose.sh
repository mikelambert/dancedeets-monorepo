#!/bin/bash

# We use without-sandbox, so that we properly load all the modules/tests
cat app.yaml | sed 's/runtime: vm/runtime: python27/' > app-nose.yaml
PYTHONPATH=lib nosetests --with-gae --gae-application=app-nose.yaml --without-sandbox --exclude="mapreduce|gdata|atom|httplib2|unittest2|simplejson|graphy" $1 $2 $3 $4 $5

