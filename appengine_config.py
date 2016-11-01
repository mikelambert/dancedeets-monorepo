import logging
import os
import sys
sys.path = [os.path.join(os.path.dirname(__file__), 'lib')] + sys.path

os.environ['GAE_USE_SOCKETS_HTTPLIB'] = '1'

# We don't need such real-time statistics (normally 1 second) on the mapreduce job.
# More of an optimization to save on the associated database Get/Put every second.
mapreduce__CONTROLLER_PERIOD_SEC = 5

appstats_MAX_STACK = 25
appstats_MAX_REPR = 100
appstats_MAX_LOCALS = 5

appstats_RECORD_FRACTION = 1.0

appstats_DATASTORE_DETAILS = True
