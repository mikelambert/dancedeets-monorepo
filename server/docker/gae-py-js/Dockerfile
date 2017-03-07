# This basically pulls from:
# https://github.com/GoogleCloudPlatform/python-compat-runtime/blob/master/Dockerfile
FROM gcr.io/google_appengine/python-compat-multicore

# Add the node version install script
ADD setup_node.sh /app/setup_node.sh
RUN /app/setup_node.sh

# We install this for use by node/npm itself
ADD install_node /usr/local/bin/install_node

# But let's change the final script to run node *and* python servers
ADD run-servers.sh /usr/local/bin/run-servers.sh
ENTRYPOINT ["bash", "run-servers.sh"]
