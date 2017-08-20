#!/bin/bash

cp ~/Dropbox/dancedeets/private/sentry.properties ./ios/
cp ~/Dropbox/dancedeets/private/sentry.properties ./android/
cp ~/Dropbox/dancedeets/private/fabric.properties ./android/app/

npm install

cd ios && pod install