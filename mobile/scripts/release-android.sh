#!/bin/bash

set -euo pipefail

cd android && ./gradlew assembleRelease "$@"
cd -
ls -al android/app/build/outputs/apk/app-release.apk
open android/app/build/outputs/apk/
