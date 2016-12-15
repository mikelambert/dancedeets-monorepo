#!/bin/bash

echo "Waiting for server to exit..."
while [ "$(ps aux | grep app-devserver.yaml | grep -v grep)" != "" ] ; do
  sleep 1
done
echo "Server exited"
