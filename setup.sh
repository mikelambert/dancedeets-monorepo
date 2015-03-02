#!/bin/bash

set -e

BASE_DIR=$(pwd)

TMP_DIR=/tmp/dancedeets-download/
mkdir -p $TMP_DIR

cd $TMP_DIR
curl https://bootstrap.pypa.io/get-pip.py --output $TMP_DIR/get-pip.py
sudo python $TMP_DIR/get-pip.py

# For testing, just install them locally. Depends on pip being installed.
sudo pip install nosegae
sudo pip install nose
sudo pip install webtest

# TOO OLD, broken media upload: pip install --upgrade -t $BASE_DIR/lib twitter

pip install --upgrade -t $BASE_DIR/lib \
  iso3166 \
  oauth2 \
  python-oauth2 \
  twilio==3.6.15 \
  google-api-python-client \
  gdata \
  python-gflags \
  Flask \
  WTForms-Appengine \
  wtforms \
  GoogleAppEngineCloudStorageClient \
  GoogleAppEnginePipeline \
  Graphy \
  simplejson \
  mock \
  mox
# We use twilio 3.5.2 since later versions use certificates and fail on appengine/googlecloud.
# See: http://android.amberfog.com/?tag=notsupportedonthisplatform
#
# This does not install the static files correctly, since they are not in setup.py
#  GoogleAppEngineMapReduce
# So instead, let's install the depencies manually:
#  GoogleAppEngineCloudStorageClient \
#  GoogleAppEnginePipeline \
#  Graphy \
#  simplejson \
#  mock \
#  mox
# We re-list them down here, since we can't stick comments inside of the \-joined command above.

function install-git() {
	cd $TMP_DIR
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
		cp -Rf $MODULE $BASE_DIR/lib/
	done
}

function install-hg() {
	cd $TMP_DIR
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
		cp -Rf $MODULE $BASE_DIR/lib/
	done
}

function install-gcode-svn() {
	cd $TMP_DIR
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
		cp -Rf $MODULE $BASE_DIR/lib/
	done
}

# Because the current published version has a bug with media uploads
install-git https://github.com/sixohsix/twitter.git twitter

# Because the published version doesn't install static files with a pip install
install-git https://github.com/GoogleCloudPlatform/appengine-mapreduce.git python/src/mapreduce

# Because there is no pip package for this
install-gcode-svn spitfire spitfire

# OAUTH2 (for authorizing twitter)
# SIX (for TWILIO)
#install-git https://github.com/deactivated/python-iso3166.git iso3166
#install-git https://github.com/simplegeo/python-oauth2.git oauth2
#install-git https://github.com/twilio/twilio-python.git twilio
#install-git https://github.com/simplejson/simplejson.git simplejson

#install-hg https://mikelambert@bitbucket.org/gutworth/six/ six.py
#install-hg https://code.google.com/p/google-api-python-client/ apiclient oauth2client uritemplate
#install-hg https://code.google.com/p/httplib2/ python2/httplib2
#install-hg https://code.google.com/p/gdata-python-client/ src/atom src/gdata

#install-gcode-svn python-gflags gflags.py gflags_validators.py
#install-gcode-svn graphy graphy

# Build our code
cd $BASE_DIR
make
