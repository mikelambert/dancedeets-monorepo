#!/bin/bash

set -euo pipefail

cd android && ./gradlew assembleRelease $1
cd -
ls -al android/app/build/outputs/apk/app-release.apk
open android/app/build/outputs/apk/