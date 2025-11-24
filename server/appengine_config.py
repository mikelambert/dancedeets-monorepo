"""App Engine configuration for Flexible Environment.

In Flexible Environment with Docker, dependencies are installed via pip
and don't need vendor setup. This file is kept for mapreduce configuration.
"""
import logging
import os
import sys

from dancedeets.util import runtime

# Add local libraries to path if needed
lib_paths = ['lib-both']
if runtime.is_local_appengine():
    lib_paths.append('lib-local')

for lib_path in lib_paths:
    lib_dir = os.path.join(os.path.dirname(__file__), lib_path)
    if os.path.exists(lib_dir) and lib_dir not in sys.path:
        sys.path.insert(0, lib_dir)

# We don't need such real-time statistics (normally 1 second) on the mapreduce job.
# More of an optimization to save on the associated database Get/Put every second.
mapreduce__CONTROLLER_PERIOD_SEC = 5
# Let's run these mapreduce tasks for longer.
# There's no reason to make them 15 seconds in an age without task runtime limits.
# And sometimes the TransientShareState goes above 1MB and can't be saved,
# resulting in an impossible-to-complete mapreduce. This just helps it avoid that.
mapreduce__SLICE_DURATION_SEC = 30

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
