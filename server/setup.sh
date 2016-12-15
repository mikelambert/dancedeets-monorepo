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
# This is installed in the docker-gae-modules, so we don't need them here.
# Having them here will break GCE, since they override the docker system modules.
# Another option is to hardcode our modules above (minus Pillow) and use --no-deps:
# https://stackoverflow.com/questions/33441033/pip-install-to-custom-target-directory-and-exclude-specific-dependencies
rm -rf lib/Pillow* lib/PIL

# So we can import zope.interface
touch $BASE_DIR/lib/zope/__init__.py
# So we can import ruamel.yaml
touch $BASE_DIR/lib/ruamel/__init__.py

# TODO: install node
# TODO: install npm?
echo "Copying over private configs"
if [ "$TRAVIS" != true ]; then
  cp ~/Dropbox/dancedeets/private/*.yaml $BASE_DIR/
fi

echo "Installing npm modules"
cd $BASE_DIR
npm install

# Now point directly to the common/ module, instead of using the installed version
rm -rf node_modules/dancedeets-common
ln -s ../../common node_modules/dancedeets-common

cd $BASE_DIR/node_server
npm install

cd $BASE_DIR
if [ "$TRAVIS" == true ]; then
  echo "Compiling CSS and JS and Icons"
  gulp compile:webpack compile:favicons
else
  echo "Installing necessary brew libraries"
  brew install homebrew/science/vips --with-webp --with-graphicsmagick
  brew install graphicsmagick
  echo "Compiling everything"
  gulp compile
fi
