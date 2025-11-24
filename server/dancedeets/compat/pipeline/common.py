"""Stub for pipeline.common"""

from dancedeets.compat import LEGACY_APIS_ENABLED

if LEGACY_APIS_ENABLED:
    from pipeline.common import *
else:
    class Stub:
        """Stub common class"""
        pass
