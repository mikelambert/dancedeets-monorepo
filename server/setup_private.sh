#!/bin/bash

set -euo pipefail

BASE_DIR=$(pwd)

echo "Copying over private configs"
cp ~/Dropbox/dancedeets/git-assets/development/server/*.yaml $BASE_DIR/
cp ~/Dropbox/dancedeets/git-assets/production/server/*.yaml $BASE_DIR/
