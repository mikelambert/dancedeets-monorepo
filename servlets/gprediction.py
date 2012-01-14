import logging
import urllib

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from logic import gprediction
from servlets import tasks

class GenerateTrainingDataHandler(tasks.BaseTaskFacebookRequestHandler):
    def get(self):
        gprediction.mr_generate_training_data(self.batch_lookup)

class DownloadTrainingDataHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        logging.info("resource is %s, blob_info is %s", resource, blob_info)
        self.send_blob(blob_info, save_as=resource)

