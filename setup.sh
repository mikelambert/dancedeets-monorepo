#!/bin/bash

set -e

BASE_DIR=$(pwd)
mkdir -p download/

cd $BASE_DIR/download
curl https://bootstrap.pypa.io/get-pip.py --output get-pip.py
python get-pip.py
sudo python get-pip.py

# For testing, just install them locally. Depends on pip being installed.
sudo pip install nosegae
sudo pip install nose
sudo pip install webtest

# SPITFIRE
cd $BASE_DIR/download
svn checkout http://spitfire.googlecode.com/svn/trunk/ spitfire-read-only
cd spitfire-read-only
sudo python setup.py install
ln -sf download/spitfire-read-only/spitfire $BASE_DIR/

# APICLIENT
cd $BASE_DIR/download
hg clone https://code.google.com/p/google-api-python-client/ || echo "Already have hg client"
cd google-api-python-client
hg update
sudo python setup.py install
ln -sf download/google-api-python-client/apiclient $BASE_DIR/
ln -sf download/google-api-python-client/oauth2client $BASE_DIR/
ln -sf download/google-api-python-client/uritemplate $BASE_DIR/

# GDATA_PYTHON_CLIENT
cd $BASE_DIR/download
hg clone https://code.google.com/p/gdata-python-client/ || echo "Already have hg client"

cd gdata-python-client
hg update
sudo python setup.py install
ln -sf download/gdata-python-client/src/atom $BASE_DIR/
ln -sf download/gdata-python-client/src/gdata $BASE_DIR/

# GFLAGS
cd $BASE_DIR/download
svn checkout http://python-gflags.googlecode.com/svn/trunk/ python-gflags-read-only
cd python-gflags-read-only
sudo python setup.py install
ln -sf download/python-gflags-read-only/gflags.py $BASE_DIR/
ln -sf download/python-gflags-read-only/gflags_validators.py $BASE_DIR/

# HTTPLIB2
cd $BASE_DIR/download
hg clone https://code.google.com/p/httplib2/ || echo "Already have hg client"

cd httplib2
hg update
sudo python setup.py install
ln -sf download/httplib2/python2/httplib2 $BASE_DIR/

# MAPREDUCE
cd $BASE_DIR/download
git clone https://github.com/GoogleCloudPlatform/appengine-mapreduce.git
cd appengine-mapreduce
# no installation! just symlinking!
ln -sf download/appengine-mapreduce/python/src/mapreduce $BASE_DIR/

#GRAPHY (used by mapreduce)
cd $BASE_DIR/download
svn checkout http://graphy.googlecode.com/svn/trunk/ graphy-read-only
cd graphy-read-only
ln -sf download/graphy-read-only/graphy $BASE_DIR/

#SIMPLEJSON (used by mapreduce)
cd $BASE_DIR/download
git clone https://github.com/simplejson/simplejson.git
cd simplejson
python setup.py build
# no installation! just symlinking!
ln -sf download/simplejson/simplejson $BASE_DIR/

# Build our code
make
