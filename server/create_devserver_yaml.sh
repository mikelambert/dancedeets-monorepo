#!/bin/bash

cat app.yaml | sed 's/instances: [0-9]*/instances: 2/' > app-devserver.yaml
ENV=""
if [ "$HOT_SERVER_PORT" != "" ]; then
  echo 'Enabling hot reloader'
  ENV="  HOT_SERVER_PORT: $HOT_SERVER_PORT
$ENV"
fi

if [ "$USE_DATASTORE_EMULATOR" != "" ]; then
  echo 'Enabling datastore emulator'
  ENV="  DATASTORE_EMULATOR_HOST: localhost:8095
$ENV"
fi

if [ "$DEBUG_MEMORY_LEAKS" != "" ]; then
  echo 'Enabling memory leak debugger'
  ENV="  DEBUG_MEMORY_LEAKS: 1
$ENV"
fi

cat <<EOF >> app-devserver.yaml

env_variables:
$ENV
EOF
