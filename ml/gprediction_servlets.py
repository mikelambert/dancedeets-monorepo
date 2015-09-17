import logging
import urllib

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

import app
import base_servlet
from . import gprediction

@app.route('/tools/generate_training_data')
class GenerateTrainingDataHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        gprediction.mr_generate_training_data(self.fbl)

@app.route('/tools/download_training_data/([^/]+)?')
class DownloadTrainingDataHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        logging.info("resource is %s, blob_info is %s", resource, blob_info)
        self.send_blob(blob_info, save_as=resource)

