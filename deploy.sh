DEFAULT_VERSION="$(gcloud preview app modules list | grep \* | awk '{print $2}')"
gcloud --verbosity info preview app deploy app.yaml --set-default
gcloud preview app modules stop default --version $DEFAULT_VERSION
