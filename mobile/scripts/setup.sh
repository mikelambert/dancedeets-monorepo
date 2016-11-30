#!/bin/bash

set -e

BASE_DIR=$(pwd)

npm install

cd $BASE_DIR/ios
pod install

# Point directly to the adjacent common module, so we don't need to npm install it
rm -rf $BASE_DIR/node_modules/dancedeets-common
ln -s ../../common $BASE_DIR/node_modules/dancedeets-common

