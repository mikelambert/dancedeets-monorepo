#!/usr/bin/env python
"""Main application entry point for DanceDeets.

This module initializes the WSGI application and imports all servlets.
"""

import logging
import os
import subprocess

# Determine if we're in production mode
prod_mode = os.environ.get('GAE_ENV') == 'standard' or os.environ.get('GOOGLE_CLOUD_PROJECT')

# Check render server status at startup
def check_render_server():
    """Check if Node.js render server is running."""
    try:
        # Check if Node is installed
        node_version = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
        logging.info(f"Node.js version: {node_version.stdout.strip()} (stderr: {node_version.stderr.strip()})")
    except Exception as e:
        logging.error(f"Node.js not available: {e}")

    try:
        # Check if dist/js-server exists
        js_server_dir = '/app/dist/js-server'
        if os.path.exists(js_server_dir):
            files = os.listdir(js_server_dir)
            logging.info(f"Files in {js_server_dir}: {files[:10]}")  # First 10 files
        else:
            logging.error(f"Directory {js_server_dir} does not exist!")
    except Exception as e:
        logging.error(f"Error checking js-server dir: {e}")

    try:
        # Check if render server is responding
        import urllib.request
        import json
        req = urllib.request.Request(
            'http://localhost:8090/render',
            data=json.dumps({"path": "/app/dist/js-server/tutorialCategory.js", "serializedProps": "{}", "toStaticMarkup": False}).encode(),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = response.read().decode()
            logging.info(f"Render server response: {data[:200]}...")
    except Exception as e:
        logging.error(f"Render server NOT responding: {e}")

    try:
        # Check running processes
        ps_output = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=5)
        node_processes = [line for line in ps_output.stdout.split('\n') if 'node' in line.lower()]
        logging.info(f"Node processes running: {node_processes}")
    except Exception as e:
        logging.error(f"Error checking processes: {e}")

# Run diagnostics at startup
logging.info("=== STARTUP DIAGNOSTICS ===")
check_render_server()
logging.info("=== END DIAGNOSTICS ===")

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
from dancedeets.util.ndb_client import ndb_wsgi_middleware  # noqa: E402


def add_wsgi_middleware(app):
    """Add WSGI middleware to the application."""
    # Add NDB context for Cloud NDB
    app = ndb_wsgi_middleware(app)

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

# Alias for gunicorn (main:app)
app = application
