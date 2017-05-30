FROM gcr.io/dancedeets-hrd/gae-modules-py

# We want this fix for Python 2.7's multiprocessing.pool:
# https://github.com/python/cpython/commit/5084ff7ddfe68969d95af12075016f309718aea8#diff-2d95253d6de7bbeebbeb131c5f3aecd9
# But this is in Python 2.7.14, which won't be in Debian or GCE for a looooong time:
# https://github.com/GoogleCloudPlatform/python-compat-runtime/issues/95#issuecomment-304770651
# So instead, let's monkeypatch this file here...
ADD ./hacks/fixed_multiprocessing_pool.py /usr/lib/python2.7/multiprocessing/pool.py

ADD . /app/
