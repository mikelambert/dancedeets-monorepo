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

echo "Installing docker gae-modules* libraries"
# This is necessary for requirements.txt installing pylibmc
if [ "$TRAVIS" == true ]; then
  sudo apt-get -qq update
  sudo apt-get install -y libxml2-dev
else
  brew install libmemcached
fi
# Things we expect to be installed in our docker container
pip install --upgrade -t $BASE_DIR/lib-local -r $BASE_DIR/docker/gae-modules/requirements.txt
pip install --upgrade -t $BASE_DIR/lib-local -r $BASE_DIR/docker/gae-modules-py/requirements.txt

echo "Installing test libraries"
# For testing, just install them locally (not in the lib/ dir).
pip install --upgrade $USER_FLAG -r $BASE_DIR/test-requirements.txt

echo "Installing the libraries which don't work with gae-modules*"
pip install --upgrade -t $BASE_DIR/lib-both -r $BASE_DIR/setup-requirements.txt

# This seems to be necessary to fix this error:
# DistributionNotFound: The 'google-cloud-datastore' distribution was not found and is required by the application
pip install $USER_FLAG google-cloud-datastore

# TODO: install node
# TODO: install npm?
echo "Copying over private configs"
if [ "$TRAVIS" != true ]; then
  cp ~/Dropbox/dancedeets/private/*.yaml $BASE_DIR/
fi

echo "Installing npm modules: ../"
cd $BASE_DIR/..
npm install


echo "Installing npm modules: ../server/"
cd $BASE_DIR
npm install

# Now point directly to the common/ module, instead of using the installed version
rm -rf node_modules/dancedeets-common
ln -s ../../common node_modules/dancedeets-common

echo "Installing npm modules: ../server/node_server/"
cd $BASE_DIR/node_server
npm install

cd $BASE_DIR

# Don't try to install frankenserver on travis, since pyobjc is non-portable:
# https://bugzilla.redhat.com/show_bug.cgi?id=1032491
if [ "$TRAVIS" != true ]; then
  # Our replacement dev_appserver
  if [ ! -e $BASE_DIR/frankenserver ]; then
    git clone https://github.com/Khan/frankenserver $BASE_DIR/frankenserver
  fi
  # Install the modules that make frankenserver amazing
  cd $BASE_DIR/frankenserver && pip install $USER_FLAG -r requirements.txt
fi

cd $BASE_DIR
if [ "$TRAVIS" == true ]; then
  echo "Compiling CSS and JS and Icons"
  gulp compile:webpack compile:images:favicons compile:test-geonames
else
  echo "Installing necessary brew libraries"
  brew ls --versions homebrew/science/vips >/dev/null || brew install homebrew/science/vips --with-webp --with-graphicsmagick
  brew ls --versions graphicsmagick >/dev/null || brew install graphicsmagick
  brew ls --versions librsvg >/dev/null || brew install librsvg
  echo "Compiling everything"
  gulp compile
fi
