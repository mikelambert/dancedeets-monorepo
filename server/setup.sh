#!/bin/bash

set -euo pipefail

BASE_DIR=$(pwd)

TMP_DIR=/tmp/dancedeets-download/
mkdir -p $TMP_DIR

cd $TMP_DIR
echo "Downloading get-pip"
curl https://bootstrap.pypa.io/get-pip.py --output $TMP_DIR/get-pip.py

TRAVIS=${TRAVIS:-false}

if [ "$TRAVIS" == true ]; then
  USER_FLAG=''
else
  USER_FLAG='--user'
fi

if [ "$TRAVIS" != true ]; then
  echo "Checking if we need to update /etc/hosts"
  HOSTS_UPDATED=$(grep dev.dancedeets.com /etc/hosts || echo -n)
  if [ "$HOSTS_UPDATED" == "" ]; then
    cat <<EOF
Updating /etc/hosts to include the dev.dancedeets.com domain."
This step requires sudo to complete, though you are welcome to decline and do it yourself.
If you would like to do it yourself, please run:
  $ cat '127.0.0.1\tdev.dancedeets.com' >> /etc/hosts
...or add '127.0.0.1\tdev.dancedeets.com' (where \t is a Tab) to /etc/hosts.
EOF
    sudo bash -c "cat '127.0.0.1\tdev.dancedeets.com' >> /etc/hosts" || echo "

Not updating /etc/hosts, but please update it yourself!

"
  fi
fi

echo "Installing docker gae-modules* libraries"
# This is necessary for requirements.txt installing pylibmc
if [ "$TRAVIS" == true ]; then
  sudo apt-get -qq update
  sudo apt-get install -y libxml2-dev
else
  brew ls --versions libmemcached >/dev/null || brew install libmemcached
fi

echo "Installing pip"
python $TMP_DIR/get-pip.py $USER_FLAG
PIP=$(which pip || echo ~/Library/Python/2.7/bin/pip)

# Things we expect to be installed in our docker container
$PIP install --upgrade -t $BASE_DIR/lib-local -r $BASE_DIR/docker/gae-modules/requirements.txt
$PIP install --upgrade -t $BASE_DIR/lib-local -r $BASE_DIR/docker/gae-modules-py/requirements.txt

echo "Installing test libraries"
# For testing, just install them locally (not in the lib/ dir).
$PIP install --upgrade -t $BASE_DIR/lib-local -r $BASE_DIR/test-requirements.txt

echo "Installing the libraries which don't work with gae-modules*"
$PIP install --upgrade -t $BASE_DIR/lib-both -r $BASE_DIR/setup-requirements.txt

# We need these binaries, which only exist if we install them system-wide
$PIP install $USER_FLAG technicolor-yawn==0.2.0
$PIP install $USER_FLAG coverage==4.2

echo "Installing npm modules: ../"
cd $BASE_DIR/..
npm install

echo "Installing npm modules: ../common/"
cd $BASE_DIR/../common
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
    cd $BASE_DIR/frankenserver
    git checkout 1.9.36
  fi
  # Install the modules that make frankenserver amazing
  cd $BASE_DIR/frankenserver && $PIP install $USER_FLAG -r requirements.txt
  $PIP install -t $BASE_DIR/lib-local -r $BASE_DIR/frankenserver/requirements.txt
fi

GULP=./node_modules/gulp/bin/gulp.js

cd $BASE_DIR
if [ "$TRAVIS" == true ]; then
  echo "Compiling CSS and JS and Icons"
  $GULP compile:webpack compile:images:favicons compile:test-geonames
else
  echo "Installing necessary brew libraries"
  brew ls --versions homebrew/science/vips >/dev/null || brew install homebrew/science/vips --with-webp --with-graphicsmagick
  brew ls --versions graphicsmagick >/dev/null || brew install graphicsmagick
  brew ls --versions librsvg >/dev/null || brew install librsvg
  echo "Building cities DB"
  $GULP compile:geonames
  echo "Compiling everything"
  $GULP compile
fi
