#!/bin/bash

set -euo pipefail

BASE_DIR=$(pwd)

echo "Copying over private configs"
cp ~/Dropbox/dancedeets-development/server/*.yaml $BASE_DIR/
cp ~/Dropbox/dancedeets-production/server/*.yaml $BASE_DIR/
