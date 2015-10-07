import json

import app
import base_servlet
from . import class_models

@app.route('/classes/upload')
class ClassUploadHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def post(self):
        studio_class_data = json.loads(self.request.body)
        studio_class = class_models.StudioClass()
        for key, value in studio_class_data:
            setattr(studio_class, key, value)
        studio_class.put()
        return '200'
    
# TODO: We need to stick these in the main index? Or in an auxiliary index. (Auxiliary index for now, and just trigger searches as appropriate)
# TODO: We need to optionally return these in the API
# TODO: We need the api clients to be able to display class data
