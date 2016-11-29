# pip installs some library files that don't upload at all, so delete them here:
rm -f "lib/setuptools/script (dev).tmpl"

time yes | gcloud app deploy app.yaml "$@"

#DEFAULT_VERSION="$(gcloud app modules list | grep \* | awk '{print $2}')"
#gcloud --verbosity info app deploy app.yaml --set-default
#gcloud app modules stop default --version $DEFAULT_VERSION
