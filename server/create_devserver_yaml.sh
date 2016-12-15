#!/bin/bash

cat app.yaml | sed 's/GAE_USE_SOCKETS_HTTPLIB/x_disabled_GAE_USE_SOCKETS_HTTPLIB/' > app-devserver.yaml
if [ "$HOT_SERVER_PORT" != "" ]; then
  echo 'Enabling hot reloader!'
  cat <<EOF >> app-devserver.yaml

env_variables:
  HOT_SERVER_PORT: $HOT_SERVER_PORT
EOF
fi
