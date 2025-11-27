#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."

PROJECT=dancedeets-hrd
BASE_IMAGE=gcr.io/$PROJECT/gae-base:latest

# Check if we can build locally (requires matching platform)
# On Mac with Apple Silicon, we can't build linux/amd64 images locally
# so we skip the local build and let gcloud handle it
LOCAL_BUILD=false
if [ "$(uname -s)" = "Linux" ] || [ "$(uname -m)" = "x86_64" ]; then
    LOCAL_BUILD=true
fi

if [ "$LOCAL_BUILD" = "true" ]; then
    echo "=== Building application Docker image locally ==="
    time docker build -t gcr.io/$PROJECT/gae-app:latest .

    echo "=== Pushing application image to GCR ==="
    time docker push gcr.io/$PROJECT/gae-app:latest
else
    echo "=== Skipping local Docker build (non-x86_64 platform) ==="
    echo "    gcloud app deploy will build in the cloud"
fi

# Copy all our JS/CSS up to the static file server (if the script exists and is needed)
if [ -f "./build_tools/upload_static_files.py" ] && [ -d "dist/js" ]; then
    echo "=== Uploading static files ==="
    python3 ./build_tools/upload_static_files.py
fi

echo "=== Deploying to App Engine ==="
# Deploy app.yaml (and batch.yaml if it exists)
if [ -f "batch.yaml" ]; then
    # Deploy batch.yaml in background with a delay to avoid AppLock conflicts
    sleep 30 && time gcloud app deploy --quiet --project $PROJECT batch.yaml "$@" &
fi

time gcloud app deploy --project $PROJECT app.yaml "$@"

echo "=== Deployment complete! ==="
echo "View at: https://$PROJECT.appspot.com"
