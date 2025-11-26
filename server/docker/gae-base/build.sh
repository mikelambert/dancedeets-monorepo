#!/bin/bash
set -e

cd "$(dirname "$0")"

# Build and push the base image
docker build -t gcr.io/dancedeets-hrd/gae-base:latest .
docker push gcr.io/dancedeets-hrd/gae-base:latest

echo "Base image built and pushed successfully!"
