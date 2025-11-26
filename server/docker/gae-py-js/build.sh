#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

export NAME=gae-py-js
export PROJECT=dancedeets-hrd
export REMOTE_IMAGE=gcr.io/$PROJECT/$NAME

echo "=== Building $NAME using Cloud Build ==="

# Use Google Cloud Build for linux/amd64 builds (works from any architecture)
gcloud builds submit --project $PROJECT --tag $REMOTE_IMAGE .

echo "=== Done: $NAME ==="
