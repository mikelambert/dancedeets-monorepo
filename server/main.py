#!/usr/bin/env python

import logging
import os
import sys

prod_mode = 'SERVER_SOFTWARE' in os.environ and not os.environ['SERVER_SOFTWARE'].startswith('Dev')

# Need to do this after vendoring lib-local/
# And can't do it in appengine_config, since that gets loaded by appengine/api/lib_config
# in places where we can't actually load pylibmc
from services import memcache

if not prod_mode:
    # Make python-twitter work in the sandbox (not yet sure about prod...)
    #import google
    #google.__file__ = ''
    #from google.appengine.tools.devappserver2.python import sandbox
    #sandbox._WHITE_LIST_C_MODULES += ['_ssl']

    # Remove the import hooks that disable C modules and built-in modules (popen et al)
    new_path = []
    for path in sys.meta_path:
        name = path.__class__.__name__
        if name not in ['StubModuleImportHook', 'CModuleImportHook']:
            new_path.append(path)
    logging.info('Trimmed sys.meta_path from %s to %s entries', len(sys.meta_path), len(new_path))
    sys.meta_path = new_path

from hacks import fixed_jinja2  # noqa: ignore=E402
from hacks import fixed_ndb  # noqa: ignore=E402
from hacks import fixed_mapreduce_util  # noqa: ignore=E402
from hacks import memory_leaks  # noqa: ignore=E402
from requests_toolbelt.adapters import appengine as appengine_adapter  # noqa: ignore=E402
from requests.packages.urllib3.contrib import appengine as appengine_manager  # noqa: ignore=E402

try:
    from google.appengine.ext.vmruntime import middlewares
except:
    if prod_mode:
        logging.error("Failed to import google.appengine.ext.vmruntime.middlewares")
else:
    middlewares.MAX_CONCURRENT_REQUESTS = 30  # Normally 501

# Disabled for now
fixed_ndb.patch_logging(0)

# Fix our runaway mapreduces
fixed_ndb.fix_rpc_ordering()

# Improve jinja2 stacktraces
fixed_jinja2.fix_stacktraces()

# Fix mapreduce to not require a certain version
fixed_mapreduce_util.patch_function()

# Make requests work with AppEngine's URLFetch
if appengine_manager.is_local_appengine():
    appengine_adapter.monkeypatch()


# Normally we'd set this up in appengine_config.py using webapp_add_wsgi_middleware
# But the imports haven't been properly set up by then, so we can't safely run this code there
# So instead, let's add the middleware directly, ourselves
def add_wsgi_middleware(app):
    # Disable appstats since it may be resulting in NDB OOM issues
    # from google.appengine.ext.appstats import recording
    # app = recording.appstats_wsgi_middleware(app)

    # Clean up per-thread NDB memory "leaks", though don't try to finish all RPCs calls (which includes runaway iterators)
    app = fixed_ndb.tasklets_toplevel(app)

    # Should only use this in cases of serialized execution of requests in a multi-threaded processes.
    # So setdeploy manually, and test from there. Never a live server, as it would be both broken *and* slow.
    if os.environ.get('DEBUG_MEMORY_LEAKS'):
        app = memory_leaks.leak_middleware(app)

    return app


if os.environ.get('HOT_SERVER_PORT'):
    logging.info('Using hot reloader!')

# Load this first, so 'app.prod_mode' is set asap
from app import app as application
application.debug = True
application.prod_mode = prod_mode
application = add_wsgi_middleware(application)

logging.info("Begin modules")
import webapp2
from google.appengine.ext.ndb import tasklets

# We call this here to force loading _strptime module upfront,
# because once threads come online and call strptime(), they try to load _strptime lazily,
# and the second thread to call it while the first one is loading with the lock, triggers an exception.
# More info:
# http://bugs.python.org/issue7980
# http://code-trick.com/python-bug-attribute-error-_strptime/
import _strptime

# We import for the side-effects in adding routes to the wsgi app
logging.info("Begin servlets")
import all_servlets
logging.info("Finished servlets")
