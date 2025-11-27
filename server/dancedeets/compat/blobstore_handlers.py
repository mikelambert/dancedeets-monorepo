"""
Stub module for Google App Engine Blobstore handlers.
This provides the interface without the implementation to allow code to import
without errors when the legacy library is not available.
"""

import logging
from dancedeets.compat import LEGACY_APIS_ENABLED

if LEGACY_APIS_ENABLED:
    from google.appengine.ext.webapp.blobstore_handlers import *
else:
    class BlobstoreDownloadHandler:
        """Stub BlobstoreDownloadHandler - blobstore is disabled in Flex environment"""
        def send_blob(self, blob_info, save_as=None):
            logging.warning("Blobstore is disabled. Cannot send blob")

    class BlobstoreUploadHandler:
        """Stub BlobstoreUploadHandler - blobstore is disabled in Flex environment"""
        def get_uploads(self, field_name=None):
            logging.warning("Blobstore is disabled. Cannot get uploads")
            return []
