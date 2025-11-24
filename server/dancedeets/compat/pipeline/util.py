"""Stub for pipeline.util"""

from dancedeets.compat import LEGACY_APIS_ENABLED

if LEGACY_APIS_ENABLED:
    from pipeline.util import *
else:
    def _get_task_target():
        return None
