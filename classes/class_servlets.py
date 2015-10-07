import datetime
import json
import urllib
import webapp2

import app
from . import class_models

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

@app.route('/classes/upload')
class ClassUploadHandler(webapp2.RequestHandler):
    def requires_login(self):
        return False

    def initialize(self, request, response):
        super(ClassUploadHandler, self).initialize(request, response)

        if self.request.body:
            escaped_body = urllib.unquote_plus(self.request.body.strip('='))
            self.json_body = json.loads(escaped_body)
        else:
            self.json_body = None

    def post(self):
        studio_class = class_models.StudioClass()
        for key, value in self.json_body.iteritems():
            if key in ['start_time', 'end_time']:
                value = datetime.datetime.strptime(value, DATETIME_FORMAT)
            setattr(studio_class, key, value)
        studio_class.put()
        self.response.status = 200
    
# TODO: We need to stick these in the main index? Or in an auxiliary index. (Auxiliary index for now, and just trigger searches as appropriate)
# TODO: We need to optionally return these in the API
# TODO: We need the api clients to be able to display class data
