import logging
import os
from google.appengine.ext import vendor
from util import runtime

vendor.add('lib-both')

if runtime.is_local_appengine():
    vendor.add('lib-local')
else:
    # Import our lib/ directory on dev only (on prod, they should be installed in the Docker image)
    os.environ['GAE_USE_SOCKETS_HTTPLIB'] = '1'

# We don't need such real-time statistics (normally 1 second) on the mapreduce job.
# More of an optimization to save on the associated database Get/Put every second.
mapreduce__CONTROLLER_PERIOD_SEC = 5
# Let's run these mapreduce tasks for 200 seconds.
# There's no reason to make them 15 seconds in an age without task runtime limits.
# And sometimes the TransientShareState goes above 1MB and can't be saved,
# resulting in an impossible-to-complete mapreduce. This just helps it avoid that.
mapreduce__SLICE_DURATION_SEC = 200

appstats_MAX_STACK = 25
appstats_MAX_REPR = 100
appstats_MAX_LOCALS = 5

appstats_RECORD_FRACTION = 1.0

appstats_DATASTORE_DETAILS = True
