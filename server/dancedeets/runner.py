#!/usr/bin/python
"""App Engine local runner example.

This program handles properly importing the App Engine SDK so that modules
can use google.appengine.* APIs and the Google App Engine testbed.
"""

import os
import sys


def fixup_paths(path):
    """Adds GAE SDK path to system path and appends it to the google path
    if that already exists."""
    # Not all Google packages are inside namespace packages, which means
    # there might be another non-namespace package named `google` already on
    # the path and simply appending the App Engine SDK to the path will not
    # work since the other package will get discovered and used first.
    # This emulates namespace packages by first searching if a `google` package
    # exists by importing it, and if so appending to its module search path.
    try:
        import google
        google.__path__.append("{0}/google".format(path))
    except ImportError:
        pass

    sys.path.insert(0, path)


def setup():
    if os.path.exists('frankenserver/python'):
        sdk_path = 'frankenserver/python'
    else:  # running on travis
        sdk_path = '../google_appengine'

    # If the SDK path points to a Google Cloud SDK installation
    # then we should alter it to point to the GAE platform location.
    if os.path.exists(os.path.join(sdk_path, 'platform/google_appengine')):
        sdk_path = os.path.join(sdk_path, 'platform/google_appengine')

    # Make sure google.appengine.* modules are importable.
    fixup_paths(sdk_path)

    # Make sure all bundled third-party packages are available.
    import dev_appserver
    dev_appserver.fix_sys_path()
    from google.appengine.ext import vendor
    vendor.add('lib-local')
    vendor.add('lib-both')

    # Loading appengine_config from the current project ensures that any
    # changes to configuration there are available to all tests (e.g.
    # sys.path modifications, namespaces, etc.)
    try:
        import appengine_config
        (appengine_config)
    except ImportError:
        print('Note: unable to import appengine_config.')
