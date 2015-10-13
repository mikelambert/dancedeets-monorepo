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
        super(JsonDataHandler, self).initialize(request, response)

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
    if not classes:
        return
    print 'De-duping classes on', classes[0].start_time.date()
    print '\n'.join(['  %s' % x.teacher.encode('utf8') for x in classes])
    most_recent_scrape_time = max(x.scrape_time for x in classes)
    old_classes = [x for x in classes if x.scrape_time != most_recent_scrape_time]
    ndb.delete_multi(x.key for x in old_classes)
    new_classes = [x for x in classes if x.scrape_time == most_recent_scrape_time]
    print "Kept:"
    print '\n'.join(['  %s' % x.teacher.encode('utf8') for x in new_classes])

@app.route('/classes/finish_upload')
class ClassFinishUploadhandler(JsonDataHandler):
    def post(self):
        #studio_name = self.json_body['studio_name']
        studio_name = self.request.get('studio_name') or self.json_body['studio_name']
        if not studio_name:
            return
        print 'De-duping all classes for', studio_name
        historical_fixup = datetime.datetime.today() - datetime.timedelta(days=2)
        query = class_models.StudioClass.query(
            class_models.StudioClass.studio_name==studio_name,
            class_models.StudioClass.start_time > historical_fixup)
        #TODO: why does this sort not work??
        # query = query.order(-class_models.StudioClass.start_time)
        results = query.fetch(1000)
        results = sorted(results, key=lambda x: x.start_time, reverse=True)
        classes_on_date = []
        processing_date = None
        # TODO: Either need infinite query that we break out of
        # Or need to bound the query with "today minus a couple days"
        #query.fetch(MAX_OBJECTS, keys_only=True)
        for studio_class in results:
            class_date = studio_class.start_time.date()
            if class_date == processing_date:
                classes_on_date.append(studio_class)
            else:
                dedupe_classes(classes_on_date)
                processing_date = class_date
                classes_on_date = [studio_class]
        dedupe_classes(classes_on_date)
        self.response.status = 200
    get=post
# TODO: We need to stick these in the main index? Or in an auxiliary index. (Auxiliary index for now, and just trigger searches as appropriate)
# TODO: We need to optionally return these in the API
# TODO: We need the api clients to be able to display class data
