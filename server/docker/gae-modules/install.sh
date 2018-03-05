set -e

cd /gae-modules/

# install memcached
apt-get update
apt-get --no-install-recommends --assume-yes install libmemcached-dev libsasl2-dev libsasl2-modules sasl2-bin

/bin/bash ./install_re2.sh

/env/bin/pip install -r ./requirements.txt
