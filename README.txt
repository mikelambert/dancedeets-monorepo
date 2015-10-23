First, download and install appengine libraries here:
https://developers.google.com/appengine/downloads
...and open the AppEngine app at least once, to set up /usr/local/google_appengine.

Second, setup gcloud:
curl https://sdk.cloud.google.com | bash
gcloud components update app preview
gcloud config set project dancedeets-hrd
gcloud auth login
gcloud preview app run app.yaml

Third, to setup dancedeets, run ./setup.sh. It will download and install libraries,
and setup some in our lib/ directory for uploading to appengine.

You can run:
- ./nose.sh to run all of the included tests.
- ./server.sh to run a local server
- ./deploy.sh to push to production

If you are running the NLP classifier evaluations, you may want to setup re2 for speed.
To do this, download/install from https://github.com/google/re2/
Then install 'pip install re2' to get the python wrappers.
