#!/bin/bash

# Use > 1 to consume two arguments per pass in the loop (e.g. each
# argument has a corresponding value to go with it).
# Use > 0 to consume one or more arguments per pass in the loop (e.g.
# some arguments don't have a corresponding value to go with it such
# as in the --default example).
# note: if this is set to > 0 the /etc/hosts part is not recognized ( may be a bug )
while [[ $# > 0 ]]
do
key="$1"
case $key in
    -c|--coverage)
    COVERAGE_PREFIX="coverage run"
    ;;
    *)
            # unknown option
    ;;
esac
shift # past argument or value
done

# We use without-sandbox, so that we properly load all the modules/tests
cat app.yaml | sed 's/runtime: vm/runtime: python27/' > app-nose.yaml
rm -rf lib/tests # this is pulled in via twilio, and messes with our excludes
MODULES=$(find lib -maxdepth 1 | grep -v info | cut -f2- -d/ | sed 's/\.py//' | paste -s -d "|" -)
PYTHONPATH=lib $COVERAGE_PREFIX `which nosetests` --with-gae --gae-application=app-nose.yaml --exclude="$MODULES" $1 $2 $3 $4 $5
