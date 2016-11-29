#!/usr/bin/env python

import logging
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))


prod_mode = 'SERVER_SOFTWARE' in os.environ and not os.environ['SERVER_SOFTWARE'].startswith('Dev')

# Make python-twitter work in the sandbox (not yet sure about prod...)
if not prod_mode:
    from google.appengine.tools.devappserver2.python import sandbox
    sandbox._WHITE_LIST_C_MODULES += ['_ssl']


from hacks import fixed_jinja2  # noqa: ignore=E402
from hacks import fixed_ndb  # noqa: ignore=E402
from hacks import fixed_mapreduce_util  # noqa: ignore=E402
from requests_toolbelt.adapters import appengine as appengine_adapter  # noqa: ignore=E402
from requests.packages.urllib3.contrib import appengine as appengine_manager  # noqa: ignore=E402

try:
    from google.appengine.ext.vmruntime import middlewares
except:
    logging.error("Failed to import google.appengine.ext.vmruntime.middlewares")
else:
    middlewares.MAX_CONCURRENT_REQUESTS = 30 # Normally 501

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


def webapp_add_wsgi_middleware(app):
    # Disable appstats since it may be resulting in NDB OOM issues
    # from google.appengine.ext.appstats import recording
    # app = recording.appstats_wsgi_middleware(app)

    # Clean up per-thread NDB memory "leaks", though don't try to finish all RPCs calls (which includes runaway iterators)
    app = fixed_ndb.tasklets_toplevel(app)

    # Should only use this in cases of serialized execution of requests in a multi-threaded processes.
    # So setdeploy manually, and test from there. Never a live server, as it would be both broken *and* slow.
    # from hacks import memory_leaks
    # app = memory_leaks.leak_middleware(app)

    return app


def is_local_appengine():
    return ('APPENGINE_RUNTIME' in os.environ and
            'Development/' in os.environ['SERVER_SOFTWARE'])

from react.conf import settings
settings.configure(
    # We want to always use the render server, since we may be rendering things that we aren't sending clientside code to render
    RENDER=True,
    RENDER_URL='http://localhost:8090/render',
)


logging.info("Begin modules")
import webapp2
from google.appengine.ext import ereporter
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

if prod_mode:
    ereporter.register_logger()

from app import app
app.debug = True
app.prod_mode = prod_mode

application = app
