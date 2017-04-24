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
# Let's run these mapreduce tasks for longer.
# There's no reason to make them 15 seconds in an age without task runtime limits.
# And sometimes the TransientShareState goes above 1MB and can't be saved,
# resulting in an impossible-to-complete mapreduce. This just helps it avoid that.
mapreduce__SLICE_DURATION_SEC = 60

# Ugh, we are running a super-long mapreduce for now. Let's avoid failures...eventually we'll reduce these.
# How many times to re-attempt the data in this slice, before giving up and restarting the entire shard
mapreduce_TASK_MAX_DATA_PROCESSING_ATTEMPTS = 1000
# How many times to re-attempt this shard as a whole, before giving up and aborting the entire mapreduce
mapreduce_SHARD_MAX_ATTEMPTS = 1000
# How many times to re-attempt this task (outside of the data-processing attempts), before giving up and aborting the entire mapreudce
mapreduce_TASK_MAX_ATTEMPTS = 1000

appstats_MAX_STACK = 25
appstats_MAX_REPR = 100
appstats_MAX_LOCALS = 5

appstats_RECORD_FRACTION = 1.0

appstats_DATASTORE_DETAILS = True
