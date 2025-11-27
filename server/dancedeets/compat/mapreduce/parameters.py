"""Stub for mapreduce.parameters"""

from dancedeets.compat import LEGACY_APIS_ENABLED

if LEGACY_APIS_ENABLED:
    from mapreduce.parameters import *
else:
    _MAX_LEASE_DURATION_SEC = 60

    class config:
        _SLICE_DURATION_SEC = 15
