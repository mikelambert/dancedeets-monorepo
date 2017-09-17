#!/bin/bash

set -euo pipefail

BASE_DIR=$(pwd)

TMP_DIR=/tmp/dancedeets-download
mkdir -p $TMP_DIR

TRAVIS=${TRAVIS:-false}

if [ "$TRAVIS" == true ]; then
  USER_FLAG=''
else
  USER_FLAG='--user'
fi



npm install

echo "Downloading get-pip"
curl https://bootstrap.pypa.io/get-pip.py --output $TMP_DIR/get-pip.py

python $TMP_DIR/get-pip.py $USER_FLAG
PIP=$(which pip || echo ~/Library/Python/2.7/bin/pip)

# Things we expect to be installed in our docker container
$PIP install --upgrade -t $BASE_DIR/lib-local -r $BASE_DIR/requirements.txt
$PIP install --upgrade -t $BASE_DIR/lib-local -r $BASE_DIR/shub-requirements.txt
