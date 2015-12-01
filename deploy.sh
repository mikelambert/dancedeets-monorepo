# pip installs some library files that don't upload at all, so delete them here:
rm -f "lib/setuptools/script (dev).tmpl"

time yes | gcloud preview app deploy app.yaml --docker-build=remote "$@"

#DEFAULT_VERSION="$(gcloud preview app modules list | grep \* | awk '{print $2}')"
#gcloud --verbosity info preview app deploy app.yaml --set-default
#gcloud preview app modules stop default --version $DEFAULT_VERSION
