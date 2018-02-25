#!/bin/bash

ARGS=()

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
    ARGS+=($key)
    ;;
esac
shift # past argument or value
done
PYTHONPATH=. APPLICATION_ID=dancedeets-hrd $COVERAGE_PREFIX $(dirname $0)/testrunner.py ${ARGS[@]}
