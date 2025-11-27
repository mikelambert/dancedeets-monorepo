"""
Stub module for Google App Engine MapReduce library.
This provides the interface without the implementation to allow code to import
without errors when the legacy library is not available.
"""

from dancedeets.compat import LEGACY_APIS_ENABLED

if LEGACY_APIS_ENABLED:
    # Re-export real mapreduce if enabled
    from mapreduce import *
else:
    # Provide stub implementation
    pass
