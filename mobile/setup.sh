#!/bin/bash

cp ~/Dropbox/dancedeets-production/mobile/sentry.properties ./ios/
cp ~/Dropbox/dancedeets-production/mobile/sentry.properties ./android/
cp ~/Dropbox/dancedeets-production/mobile/fabric.properties ./android/app/

npm install

cd ios && pod install