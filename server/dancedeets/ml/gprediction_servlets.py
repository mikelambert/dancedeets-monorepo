import logging
import urllib.parse

from flask import Response, send_file
from google.cloud import storage
import io

from dancedeets import app
from dancedeets import base_servlet
from . import gprediction

# GCS bucket name - should match the bucket where training data is stored
GCS_BUCKET_NAME = 'dancedeets-hrd.appspot.com'


@app.route('/tools/generate_training_data')
class GenerateTrainingDataHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        gprediction.mr_generate_training_data(self.fbl)


@app.route('/tools/download_training_data/<path:resource>')
class DownloadTrainingDataHandler(base_servlet.BareBaseRequestHandler):
    def get(self, resource):
        resource = str(urllib.parse.unquote(resource))
        logging.info("Downloading resource: %s", resource)

        try:
            # Initialize GCS client
            client = storage.Client()
            bucket = client.bucket(GCS_BUCKET_NAME)
            blob = bucket.blob(resource)

            if not blob.exists():
                logging.error("Resource not found: %s", resource)
                self.response.status = 404
                self.response.out.write('Resource not found')
                return

            # Download the blob content to memory
            content = blob.download_as_bytes()

            # Set appropriate headers for download
            self.response.headers['Content-Type'] = blob.content_type or 'application/octet-stream'
            self.response.headers['Content-Disposition'] = f'attachment; filename="{resource}"'
            self.response.out.write(content)

        except Exception as e:
            logging.error("Error downloading resource %s: %s", resource, e)
            self.response.status = 500
            self.response.out.write(f'Error: {e}')
