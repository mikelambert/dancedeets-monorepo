#!/bin/bash

cat app.yaml | sed 's/instances: [0-9]*/instances: 1/' | sed 's/service: default/service: memory/' > app-memory.yaml

cat <<EOF >> app-memory.yaml

env_variables:
  DEBUG_MEMORY_LEAKS: 1
EOF
