import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

from hacks import fixed_ndb
from hacks import fixed_mapreduce_util
from requests_toolbelt.adapters import appengine as appengine_adapter
from requests.packages.urllib3.contrib import appengine as appengine_manager
fixed_mapreduce_util.patch_function()

# Disabled for now
fixed_ndb.patch_logging(0)

# Fix our runaway mapreduces
fixed_ndb.fix_rpc_ordering()

# Make requests work with AppEngine's URLFetch
if appengine_manager.is_local_appengine():
    appengine_adapter.monkeypatch()

def webapp_add_wsgi_middleware(app):
    #from google.appengine.ext.ndb import tasklets
    from google.appengine.ext.appstats import recording

    app = recording.appstats_wsgi_middleware(app)

    # Clean up per-thread NDB memory "leaks", though don't try to finish all RPCs calls (which includes runaway iterators)
    app = fixed_ndb.tasklets_toplevel(app)

    # Should only use this in cases of serialized execution of requests in a multi-threaded processes.
    # So setdeploy manually, and test from there. Never a live server, as it would be both broken *and* slow.
    # from hacks import memory_leaks
    #app = memory_leaks.leak_middleware(app)

    return app

# We don't need such real-time statistics (normally 1 second) on the mapreduce job.
# More of an optimization to save on the associated database Get/Put every second.
mapreduce__CONTROLLER_PERIOD_SEC = 5

appstats_MAX_STACK = 25
appstats_MAX_REPR = 100
appstats_MAX_LOCALS = 5

appstats_RECORD_FRACTION = 1.0

appstats_DATASTORE_DETAILS = True
