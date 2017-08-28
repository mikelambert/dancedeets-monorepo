#!/bin/bash

set -euo pipefail

BASE_DIR=$(pwd)

pip install --upgrade -t $BASE_DIR/lib google-cloud-datastore apache-beam
