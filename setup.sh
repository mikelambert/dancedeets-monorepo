#!/bin/bash

set -e

BASE_DIR=$(pwd)

TMP_DIR=/tmp/dancedeets-download/
mkdir -p $TMP_DIR

cd $TMP_DIR
echo "Downloading get-pip"
curl https://bootstrap.pypa.io/get-pip.py --output $TMP_DIR/get-pip.py

if [ "$TRAVIS" == true ]; then
  USER_FLAG=''
else
  USER_FLAG='--user'
fi

echo "Installing pip"
python $TMP_DIR/get-pip.py $USER_FLAG

echo "Installing docker-gae-modules libraries"
# Things we expect to be installed in our docker container
pip install --upgrade $USER_FLAG -r $BASE_DIR/docker-gae-modules/requirements.txt

echo "Installing test libraries"
# For testing, just install them locally (not in the lib/ dir).
pip install --upgrade $USER_FLAG -r $BASE_DIR/test-requirements.txt

echo "Installing production libraries"
pip install --upgrade -t $BASE_DIR/lib -r $BASE_DIR/setup-requirements.txt

# So we can import zope.interface
touch $BASE_DIR/lib/zope/__init__.py

# TODO: install node
# TODO: install npm?

cd $BASE_DIR

echo "Installing npm modules"
npm install

if [ "$TRAVIS" == true ]; then
  echo "Compiling CSS and JS"
  gulp compile-css-js compile-favicons
else
  echo "Installing necessary brew libraries"
  brew install homebrew/science/vips --with-webp --with-graphicsmagick
  brew install graphicsmagick
  echo "Compiling everything"
  gulp compile
fi
