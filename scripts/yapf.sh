#!/bin/bash

BASEDIR=$(dirname $0)/..
PYTHONPATH=$BASEDIR/server/lib-local python $BASEDIR/server/lib-local/yapf --style=$BASEDIR/.style.yapf $1 $2 $3 $4 $5 $6 $7 $8 $9