#!/bin/bash

# We use without-sandbox, so that we properly load all the modules/tests
cat app.yaml | sed 's/runtime: vm/runtime: python27/' > app-nose.yaml
rm -rf lib/tests # this is pulled in via twilio, and messes with our excludes
PYTHONPATH=lib nosetests --with-gae --gae-application=app-nose.yaml --without-sandbox --exclude="flask_admin|werkzeug|flask|markupsafe|jinja2|oauth2|mapreduce|gdata|atom|httplib2|unittest2|simplejson|graphy|requests|rsa" $1 $2 $3 $4 $5

