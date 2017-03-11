set -e
cd `dirname $0`
export NAME=gae-app
export LOCAL_IMAGE=mlambert/$NAME
export REMOTE_IMAGE=gcr.io/dancedeets-hrd/$NAME
time docker build -t $LOCAL_IMAGE .
docker tag $LOCAL_IMAGE $REMOTE_IMAGE
time gcloud docker -- push $REMOTE_IMAGE
time gcloud app deploy --quiet --image-url $REMOTE_IMAGE
