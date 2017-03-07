# And this is a copy from:
# https://github.com/GoogleCloudPlatform/nodejs-docker/blob/master/base/Dockerfile

# Install updates and dependencies
apt-get update -y && apt-get install --no-install-recommends -y -q curl python build-essential git ca-certificates libkrb5-dev imagemagick netbase && \
    apt-get clean && rm /var/lib/apt/lists/*_*

# Install the latest LTS release of nodejs
mkdir /nodejs && curl https://nodejs.org/dist/v6.10.0/node-v6.10.0-linux-x64.tar.gz | tar xvzf - -C /nodejs --strip-components=1
export PATH=$PATH:/nodejs/bin

npm install --unsafe-perm semver
