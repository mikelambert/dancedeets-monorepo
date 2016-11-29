#!/bin/bash

set -e

BASE_DIR=$(pwd)

npm install

cd $BASE_DIR/ios
pod install
