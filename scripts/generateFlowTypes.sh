#!/usr/bin/bash

FLOW_TYPED="node $(pwd)/node_modules/flow-typed/dist/cli.js install --skip"
# FLOW_TYPED="node $(pwd)/../flow-typed/cli/dist/cli.js"
BASE_DIR="$(pwd)"

cd . && $FLOW_TYPED ; CD $BASE_DIR
cd server && $FLOW_TYPED ; cd $BASE_DIR
cd server/node_modules && $FLOW_TYPED ; cd $BASE_DIR
cd common && $FLOW_TYPED ; cd $BASE_DIR
cd mobile && $FLOW_TYPED ; cd $BASE_DIR
