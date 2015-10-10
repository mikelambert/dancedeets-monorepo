import datetime
import json
import urllib
import webapp2

from google.appengine.ext import ndb

import app
from . import class_models

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

class JsonDataHandler(webapp2.RequestHandler):
    def initialize(self, request, response):
        super(ClassUploadHandler, self).initialize(request, response)

        if self.request.body:
            escaped_body = urllib.unquote_plus(self.request.body.strip('='))
            self.json_body = json.loads(escaped_body)
        else:
            self.json_body = None


@app.route('/classes/upload')
class ClassUploadHandler(JsonDataHandler):
    def post(self):
        #TODO: check if class already exists, and update it versus creating a new one?
        #TODO: And maybe only save/reindex if there were legit changes?
        studio_class = class_models.StudioClass()
        for key, value in self.json_body.iteritems():
            if key in ['start_time', 'end_time', 'scrape_time']:
                value = datetime.datetime.strptime(value, DATETIME_FORMAT)
            setattr(studio_class, key, value)
        studio_class.put()
        self.response.status = 200

def dedupe_classes(classes):
    most_recent_scrape_time = max(x.scape_time for x in classes)
    old_classes = [x for x in classes if x.scape_time != most_recent_scrape_time]
    ndb.delete_multi(x.key for x in old_classes)

@app.route('/classes/finish_upload')
class ClassFinishUploadhandler(JsonDataHandler):
    def post(self):
        studio_name = self.json_body['studio_name']
        query = class_models.StudioClass.query(class_models.StudioClass.studio_name==studio_name)
        query = query.order(-class_models.StudioClass.start_time)
        classes_on_date = []
        processing_date = None
        for studio_class in query:
            class_date = studio_class.start_time.date()
            if class_date == processing_date:
                classes_on_date.append(studio_class)
            else:
                dedupe_classes(classes_on_date)
                processing_date = class_date
                classes_on_date = [studio_class]
        dedupe_classes(classes_on_date)
        #query.fetch(MAX_OBJECTS, keys_only=True)
        self.response.status = 200

# TODO: We need to stick these in the main index? Or in an auxiliary index. (Auxiliary index for now, and just trigger searches as appropriate)
# TODO: We need to optionally return these in the API
# TODO: We need the api clients to be able to display class data
