#!/usr/bin/env python

import logging
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

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


prod_mode = 'SERVER_SOFTWARE' in os.environ and not os.environ['SERVER_SOFTWARE'].startswith('Dev')

# Make python-twitter work in the sandbox (not yet sure about prod...)
if not prod_mode:
    from google.appengine.tools.devappserver2.python import sandbox
    sandbox._WHITE_LIST_C_MODULES += ['_ssl']

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
