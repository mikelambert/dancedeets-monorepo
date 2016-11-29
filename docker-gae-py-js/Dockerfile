# This basically pulls from:
# https://github.com/GoogleCloudPlatform/python-compat-runtime/blob/master/Dockerfile
FROM gcr.io/google_appengine/python-compat-multicore

# And this is a copy from:
# https://github.com/GoogleCloudPlatform/nodejs-docker/blob/master/base/Dockerfile

# Install updates and dependencies
RUN apt-get update -y && apt-get install --no-install-recommends -y -q curl python build-essential git ca-certificates libkrb5-dev imagemagick && \
    apt-get clean && rm /var/lib/apt/lists/*_*

# Install the latest LTS release of nodejs
RUN mkdir /nodejs && curl https://nodejs.org/dist/v6.9.1/node-v6.9.1-linux-x64.tar.gz | tar xvzf - -C /nodejs --strip-components=1
ENV PATH $PATH:/nodejs/bin

# Install semver, as required by the node version install script.
RUN npm install https://storage.googleapis.com/gae_node_packages/semver.tar.gz

# Add the node version install script
ADD install_node /usr/local/bin/install_node

# Set common env vars
ENV NODE_ENV production




# But let's change the final script to run node *and* python servers
ADD run-servers.sh /usr/local/bin/run-servers.sh
ENTRYPOINT ["bash", "run-servers.sh"]

