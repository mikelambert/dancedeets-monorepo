#!/usr/bin/python
"""App Engine local runner for Flexible Environment.

This program handles properly setting up paths for local development and testing.
In Flexible Environment with Docker, most dependencies are installed via pip.
"""

import os
import sys


def setup():
    """Set up the environment for running locally or in tests."""
    # Add local library directories to path
    base_path = os.path.dirname(os.path.dirname(__file__))

    lib_paths = ['lib-local', 'lib-both']
    for lib_path in lib_paths:
        full_path = os.path.join(base_path, lib_path)
        if os.path.exists(full_path) and full_path not in sys.path:
            sys.path.insert(0, full_path)

    # Try to set up the Google Cloud NDB client context for local testing
    try:
        from google.cloud import ndb
        # For local development, you may need to set up credentials
        # export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
    except ImportError:
        pass

    # Loading appengine_config from the current project ensures that any
    # changes to configuration there are available to all tests (e.g.
    # sys.path modifications, namespaces, etc.)
    try:
        import appengine_config
        (appengine_config)
    except ImportError:
        print('Note: unable to import appengine_config.')
