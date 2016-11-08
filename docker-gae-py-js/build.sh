export LOCAL_IMAGE=mlambert/gae-py-js
export REMOTE_IMAGE=us.gcr.io/dancedeets-hrd/gae-py-js
docker build -t $LOCAL_IMAGE .
docker tag $LOCAL_IMAGE $REMOTE_IMAGE
gcloud docker -- push $REMOTE_IMAGE
