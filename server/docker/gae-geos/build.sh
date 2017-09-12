set -euo pipefail
cd `dirname $0`
export NAME=gae-geos
export LOCAL_IMAGE=mlambert/$NAME
export REMOTE_IMAGE=gcr.io/dancedeets-hrd/$NAME
docker build --no-cache -t $LOCAL_IMAGE .
docker tag $LOCAL_IMAGE $REMOTE_IMAGE
gcloud docker -- push $REMOTE_IMAGE
