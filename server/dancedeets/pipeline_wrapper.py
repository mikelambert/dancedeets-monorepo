#!/usr/bin/env python
"""Pipeline wrapper for Flexible Environment.

Sets up the path and loads the pipeline handlers.
In Flexible Environment with Docker, dependencies are installed via pip.
"""

import os
import sys

from dancedeets.util import runtime

# Add local libraries to path if needed
base_path = os.path.dirname(os.path.dirname(__file__))
lib_paths = ['lib-both']
if runtime.is_local_appengine():
    lib_paths.append('lib-local')

for lib_path in lib_paths:
    full_path = os.path.join(base_path, lib_path)
    if os.path.exists(full_path) and full_path not in sys.path:
        sys.path.insert(0, full_path)

from pipeline.handlers import _APP

# Disables the pipeline auth checking, since we now handle that ourselves
import pipeline
pipeline.set_enforce_auth(False)
