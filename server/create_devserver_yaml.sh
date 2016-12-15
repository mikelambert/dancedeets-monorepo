#!/bin/bash

cat app.yaml | sed 's/GAE_USE_SOCKETS_HTTPLIB/x_disabled_GAE_USE_SOCKETS_HTTPLIB/' > app-devserver.yaml
if [ "$HOT" = "1" ]; then
  echo 'Enabling hot reloader!'
  cat <<EOF >> app-devserver.yaml

env_variables:
  HOT_SERVER_PORT: 9090
EOF
fi