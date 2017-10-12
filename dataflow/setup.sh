#!/bin/bash

set -euo pipefail

BASE_DIR=$(pwd)

pip install --upgrade -t $BASE_DIR/lib \
  google-cloud-datastore==1.3.0 \
  apache-beam==2.1.1 \
  google-apitools==0.5.16
