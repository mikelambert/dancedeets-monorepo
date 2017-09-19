FROM gcr.io/dancedeets-hrd/gae-modules-py

# Build for GAE Flex deployment
# Depends on the dockerfiles built in docker/

# We want this fix for Python 2.7's multiprocessing.pool:
# https://github.com/python/cpython/commit/5084ff7ddfe68969d95af12075016f309718aea8#diff-2d95253d6de7bbeebbeb131c5f3aecd9
# But this is in Python 2.7.14, which won't be in Debian or GCE for a looooong time:
# https://github.com/GoogleCloudPlatform/python-compat-runtime/issues/95#issuecomment-304770651
# So instead, let's monkeypatch this file here...
ADD ./dancedeets/hacks/fixed_multiprocessing_pool.py /usr/lib/python2.7/multiprocessing/pool.py

# But let's change the final script to run node *and* python *and* nginx servers
ADD run-servers.sh /usr/local/bin/run-servers.sh
ENTRYPOINT ["bash", "run-servers.sh"]

ADD . /app/
