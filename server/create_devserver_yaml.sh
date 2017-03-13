#!/bin/bash

cat app.yaml | sed 's/instances: [0-9]*/instances: 1/' > app-devserver.yaml
if [ "$HOT_SERVER_PORT" != "" ]; then
  echo 'Enabling hot reloader!'
  cat <<EOF >> app-devserver.yaml

env_variables:
  HOT_SERVER_PORT: $HOT_SERVER_PORT
EOF
fi
