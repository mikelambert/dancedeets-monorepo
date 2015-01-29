#!/bin/bash

set -e

BASE_DIR=$(pwd)
mkdir -p download/

cd $BASE_DIR/download
curl https://bootstrap.pypa.io/get-pip.py --output get-pip.py
#python get-pip.py
sudo python get-pip.py

# For testing, just install them locally. Depends on pip being installed.
sudo pip install nosegae
sudo pip install nose
sudo pip install webtest

function install-git() {
	cd $BASE_DIR/download
	REPO_PATH=$1
	shift
	echo
	echo $REPO_PATH
	echo
	REPO_FILENAME=$(basename $REPO_PATH)
	REPO_DIRNAME="${REPO_FILENAME%.*}"
	[ -e $REPO_DIRNAME ] || git clone $REPO_PATH
	cd $REPO_DIRNAME
	git pull
	[ -e setup.py ] && python setup.py build
	for MODULE in $*
	do
		[ -h $BASE_DIR/$(basename $MODULE) ] && rm $BASE_DIR/$(basename $MODULE)
		cp -Rf $MODULE $BASE_DIR/
	done
}

function install-hg() {
	cd $BASE_DIR/download
	REPO_PATH=$1
	shift
	echo
	echo $REPO_PATH
	echo
	REPO_DIRNAME=$(basename $REPO_PATH)
	[ -e $REPO_DIRNAME ] || hg clone $REPO_PATH
	cd $REPO_DIRNAME
	hg update
	[ -e setup.py ] && python setup.py build
	for MODULE in $*
	do
		[ -h $BASE_DIR/$(basename $MODULE) ] && rm $BASE_DIR/$(basename $MODULE)
		cp -Rf $MODULE $BASE_DIR/
	done
}

function install-gcode-svn() {
	cd $BASE_DIR/download
	REPO_PATH=$1
	shift
	echo
	echo $REPO_PATH
	echo
	REPO_DIRNAME="${REPO_PATH}-read-only"
	svn checkout http://$REPO_PATH.googlecode.com/svn/trunk/ $REPO_DIRNAME
	cd $REPO_DIRNAME
	svn up
	[ -e setup.py ] && python setup.py build
	for MODULE in $*
	do
		[ -h $BASE_DIR/$(basename $MODULE) ] && rm $BASE_DIR/$(basename $MODULE)
		cp -Rf $MODULE $BASE_DIR/
	done
}

# OAUTH2 (for authorizing twitter)
install-git https://github.com/deactivated/python-iso3166.git iso3166
install-git https://github.com/sixohsix/twitter.git twitter
install-git https://github.com/simplegeo/python-oauth2.git oauth2
install-git https://github.com/twilio/twilio-python.git twilio
install-git https://github.com/simplejson/simplejson.git simplejson
install-git https://github.com/GoogleCloudPlatform/appengine-mapreduce.git python/src/mapreduce

# SIX (for TWILIO)
install-hg https://mikelambert@bitbucket.org/gutworth/six/ six.py
install-hg https://code.google.com/p/google-api-python-client/ apiclient oauth2client uritemplate
install-hg https://code.google.com/p/httplib2/ python2/httplib2
install-hg https://code.google.com/p/gdata-python-client/ src/atom src/gdata

install-gcode-svn spitfire spitfire
install-gcode-svn python-gflags gflags.py gflags_validators.py
install-gcode-svn graphy graphy

# Build our code
cd $BASE_DIR
make
