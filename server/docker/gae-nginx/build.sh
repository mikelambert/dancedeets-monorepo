#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

export NAME=gae-nginx
export PROJECT=dancedeets-hrd
export REMOTE_IMAGE=gcr.io/$PROJECT/$NAME

echo "=== Building $NAME using Cloud Build ==="
gcloud builds submit --project $PROJECT --tag $REMOTE_IMAGE .

echo "=== Done: $NAME ==="
