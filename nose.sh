#!/bin/bash

rm -rf lib/tests # this is pulled in via twilio, and messes with our excludes
cat app.yaml | sed 's/runtime: vm/runtime: python27/' > /tmp/app-nose.yaml
PYTHONPATH=lib nosetests --with-gae --gae-application=/tmp/app-nose.yaml --exclude="flask_admin|werkzeug|flask|markupsafe|jinja2|oauth2|mapreduce|gdata|atom|httplib2|unittest2|simplejson|graphy|requests|rsa" $1 $2 $3 $4 $5

