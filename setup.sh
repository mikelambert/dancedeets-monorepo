#!/bin/bash

set -e

BASE_DIR=$(pwd)

TMP_DIR=/tmp/dancedeets-download/
mkdir -p $TMP_DIR

cd $TMP_DIR
curl https://bootstrap.pypa.io/get-pip.py --output $TMP_DIR/get-pip.py
sudo python $TMP_DIR/get-pip.py

# For testing, just install them locally. Depends on pip being installed.
# Install jinja2 library directly, so nlp/ libraries can be used directly
sudo pip install nosegae nose webtest jinja2 --upgrade --ignore-installed six --user

pip install --upgrade -t $BASE_DIR/lib -r $BASE_DIR/setup-requirements.txt
