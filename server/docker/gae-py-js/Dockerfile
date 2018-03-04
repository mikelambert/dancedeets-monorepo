# This basically pulls from:
# https://github.com/GoogleCloudPlatform/python-compat-runtime/blob/master/Dockerfile
# We run our own python-compat-multicore since the real one is out of date with respect to github
FROM gcr.io/dancedeets-hrd/python-compat-multicore

# Add the node version install script
ADD setup_node.sh /app/setup_node.sh
RUN /app/setup_node.sh

# We install this for use by node/npm itself
ADD install_node /usr/local/bin/install_node
