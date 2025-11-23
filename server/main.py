#!/usr/bin/env python
"""Main application entry point for DanceDeets.

This module initializes the WSGI application and imports all servlets.
"""

import logging
import os

# Determine if we're in production mode
prod_mode = os.environ.get('GAE_ENV') == 'standard' or os.environ.get('GOOGLE_CLOUD_PROJECT')

# Initialize memcache
from dancedeets.services import memcache  # noqa: E402

# Import hacks/patches (these will need to be updated for Cloud NDB)
try:
    from dancedeets.hacks import fixed_jinja2
    fixed_jinja2.fix_stacktraces()
except ImportError:
    logging.warning('fixed_jinja2 not available')

try:
    from dancedeets.hacks import memory_leaks
except ImportError:
    memory_leaks = None

from dancedeets.redirect_canonical import redirect_canonical  # noqa: E402


def add_wsgi_middleware(app):
    """Add WSGI middleware to the application."""
    # Memory leak debugging middleware (only in debug mode)
    if os.environ.get('DEBUG_MEMORY_LEAKS') and memory_leaks:
        app = memory_leaks.leak_middleware(app)

    # Redirect dancedeets.com to www.dancedeets.com
    return redirect_canonical(app, 'dancedeets.com', 'www.dancedeets.com')


if os.environ.get('HOT_SERVER_PORT'):
    logging.info('Using hot reloader!')

# Load the main application
from dancedeets.app import app as application  # noqa: E402
application.debug = not prod_mode
application.prod_mode = prod_mode
application = add_wsgi_middleware(application)

logging.info("Begin modules")

# Force loading _strptime module upfront to avoid threading issues
# See: http://bugs.python.org/issue7980
import _strptime  # noqa: F401

# Import servlets for their side-effects (route registration)
logging.info("Begin servlets")
import dancedeets.all_servlets  # noqa: F401, E402
logging.info("Finished servlets")
