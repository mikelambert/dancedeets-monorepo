#!/bin/bash

set -euo pipefail

BASE_DIR=$(pwd)

echo "Copying over private configs"
cp ~/Dropbox/dancedeets/private/*.yaml $BASE_DIR/
