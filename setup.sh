#!/bin/bash

# Download and install mercurial here:
# http://mercurial.selenic.com/downloads/
# Download and install appengine libraries here:
# https://developers.google.com/appengine/downloads
# ...and be sure to run it once, to set up usr/local/google_appengine

# Find latest version here: https://pypi.python.org/pypi/nose
NOSE_VERSION=nose-1.3.0
# Find latest version here: https://pypi.python.org/pypi/unittest2
UNITTEST2_VERSION=unittest2-0.5.1-python2.3
# Find latest version here: https://pypi.python.org/pypi/WebTest
WEBTEST_VERSION=WebTest-2.0.12

BASE_DIR=$(pwd)
mkdir download/

# NOSE
cd $BASE_DIR/download
curl https://pypi.python.org/packages/source/n/nose/$NOSE_VERSION.tar.gz --output $NOSE_VERSION.tar.gz
tar xvzf $NOSE_VERSION.tar.gz
cd $NOSE_VERSION
sudo python setup.py install

# NOSE-GAE
cd $BASE_DIR/download
svn checkout http://nose-gae.googlecode.com/svn/trunk/ nose-gae-read-only
cd nose-gae-read-only
sudo python setup.py install

# SPITFIRE
cd $BASE_DIR/download
svn checkout http://spitfire.googlecode.com/svn/trunk/ spitfire-read-only
cd spitfire-read-only
sudo python setup.py install
ln -s download/spitfire-read-only/spitfire $BASE_DIR/

# APICLIENT
cd $BASE_DIR/download
hg clone https://code.google.com/p/google-api-python-client/
cd google-api-python-client
sudo python setup.py install
ln -s download/google-api-python-client/apiclient $BASE_DIR/
ln -s download/google-api-python-client/oauth2client $BASE_DIR/
ln -s download/google-api-python-client/uritemplate $BASE_DIR/

# GDATA_PYTHON_CLIENT
cd $BASE_DIR/download
hg clone https://code.google.com/p/gdata-python-client/
cd gdata-python-client
sudo python setup.py install
ln -s download/gdata-python-client/src/atom $BASE_DIR/
ln -s download/gdata-python-client/src/gdata $BASE_DIR/

# GFLAGS
cd $BASE_DIR/download
svn checkout http://python-gflags.googlecode.com/svn/trunk/ python-gflags-read-only
cd python-gflags-read-only
sudo python setup.py install
ln -s download/python-gflags-read-only/gflags.py $BASE_DIR/
ln -s download/python-gflags-read-only/gflags_validators.py $BASE_DIR/

# HTTPLIB2
cd $BASE_DIR/download
hg clone https://code.google.com/p/httplib2
cd httplib2
sudo python setup.py install
ln -s download/httplib2/python2/httplib2 $BASE_DIR/

# MAPREDUCE
cd $BASE_DIR/download
svn checkout http://appengine-mapreduce.googlecode.com/svn/trunk/ appengine-mapreduce-read-only
cd appengine-mapreduce-read-only
# no installation! just symlinking!
ln -s download/appengine-mapreduce-read-only/python/src/mapreduce $BASE_DIR/

# UNITTEST2
cd $BASE_DIR/download
curl http://www.voidspace.org.uk/downloads/$UNITTEST2_VERSION.zip -o $UNITTEST2_VERSION.zip
unzip -o $UNITTEST2_VERSION.zip
cd $UNITTEST2_VERSION
sudo python setup.py install
ln -s download/$UNITTEST2_VERSION/unittest2 $BASE_DIR/

# WEBTEST
cd $BASE_DIR/download
curl https://pypi.python.org/packages/source/W/WebTest/$WEBTEST_VERSION.zip -o $WEBTEST_VERSION.zip
unzip -o $WEBTEST_VERSION
cd $WEBTEST_VERSION
sudo python setup.py install
# No symlink necessary here?
# ln -s download/$WEBTEST_VERSION/webtest $BASE_DIR
