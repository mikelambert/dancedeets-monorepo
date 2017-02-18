#!/bin/bash

# Returns success if there are no .so modules (other than our safe optional ones)
! FILES=$(find lib -name '*.so' | grep -v /_speedups.so)
RESULT=$?

if [ -n "$FILES" ]; then
    >&2 echo 'Found unexpected .so files:'
    >&2 echo $FILES
fi

exit $RESULT
