"""
Stub module for Google App Engine Blobstore library.
This provides the interface without the implementation to allow code to import
without errors when the legacy library is not available.
"""

import logging
from dancedeets.compat import LEGACY_APIS_ENABLED

if LEGACY_APIS_ENABLED:
    from google.appengine.ext.blobstore import *
else:
    class BlobInfo:
        """Stub BlobInfo"""
        @staticmethod
        def get(resource):
            logging.warning("Blobstore is disabled. Cannot get blob: %s", resource)
            return None

    class BlobKey:
        """Stub BlobKey"""
        def __init__(self, key):
            self.key = key

    def create_upload_url(success_path, **kwargs):
        logging.warning("Blobstore is disabled. Cannot create upload url")
        return None
