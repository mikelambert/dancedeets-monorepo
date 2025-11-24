"""Stub for mapreduce.input_readers"""

from dancedeets.compat import LEGACY_APIS_ENABLED

if LEGACY_APIS_ENABLED:
    from mapreduce.input_readers import *
else:
    # Sentinel value used by mapreduce
    ALLOW_CHECKPOINT = object()

    class DatastoreInputReader:
        """Stub DatastoreInputReader"""
        pass

    class InputReader:
        """Stub InputReader"""
        pass

    class GoogleCloudStorageInputReader:
        """Stub GoogleCloudStorageInputReader"""
        pass
