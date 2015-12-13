#!/bin/bash

# We use without-sandbox, so that we properly load all the modules/tests
cat app.yaml | sed 's/runtime: vm/runtime: python27/' > app-nose.yaml
rm -rf lib/tests # this is pulled in via twilio, and messes with our excludes
MODULES=$(find lib -depth 1 | grep -v info | cut -f2- -d/ | sed 's/\.py//' | paste -s -d "|" -)
PYTHONPATH=lib nosetests --with-gae --gae-application=app-nose.yaml --exclude="$MODULES" $1 $2 $3 $4 $5
