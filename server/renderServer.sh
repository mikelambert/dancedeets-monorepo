#!/bin/bash

function runServer() {
  node dist/js-server/renderServer.js
}

until runServer; do
  echo "renderServer crashed with exit code $?.  Respawning..." >&2
  sleep 1
done
