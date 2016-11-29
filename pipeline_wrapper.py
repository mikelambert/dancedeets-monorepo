#!/usr/bin/env python

# Because the app.yaml handlers are imported via:
# Traceback (most recent call last):
#  File "/env/local/lib/python2.7/site-packages/vmruntime/wsgi_config.py", line 55, in app_for_script
#    app, unused_filename, err = wsgi.LoadObject(script)
#  File "/env/local/lib/python2.7/site-packages/google/appengine/runtime/wsgi.py", line 85, in LoadObject
#    obj = __import__(path[0])
# It means we have no chance to hook-in and update the sys.path before they are loaded.
# So this wrapper just does that...updates the sys.path, and loads the _APP handlers

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

from pipeline.handlers import _APP
