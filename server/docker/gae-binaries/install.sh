set -e

cd /gae-binaries/

apt-get update
apt-get --assume-yes install automake libtool
curl -L https://github.com/pornel/giflossy/archive/v1.88.tar.gz | tar xvz
#tar xvzf giflossy.tar.gz
cd giflossy-1.88/
autoreconf -i
./configure
make install
