#!/bin/bash

set -e

BASE_DIR=$(pwd)

TMP_DIR=/tmp/dancedeets-download/
mkdir -p $TMP_DIR

cd $TMP_DIR
curl https://bootstrap.pypa.io/get-pip.py --output $TMP_DIR/get-pip.py

# For testing, just install them locally. Depends on pip being installed.
USER_FLAG='--user'
echo "Travis is $TRAVIS"
if [ "$TRAVIS" == true ]; then
  USER_FLAG=''
fi

python $TMP_DIR/get-pip.py $USER_FLAG

pip install --upgrade $USER_FLAG -r $BASE_DIR/test-requirements.txt

pip install --upgrade -t $BASE_DIR/lib -r $BASE_DIR/setup-requirements.txt

# TODO: install node
# TODO: install npm?
brew install homebrew/science/vips --with-webp --with-graphicsmagick
brew install graphicsmagick

npm install

gulp compile
