#!/bin/bash

cp ~/Dropbox/dancedeets/git-assets/production/mobile/sentry.properties ./ios/
cp ~/Dropbox/dancedeets/git-assets/production/mobile/sentry.properties ./android/
cp ~/Dropbox/dancedeets/git-assets/production/mobile/fabric.properties ./android/app/

npm install

cd ios && pod install